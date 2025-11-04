// AAInspector.cpp — Works with LLVM 21
#include "llvm/IR/PassManager.h"
#include "llvm/IR/Function.h"
#include "llvm/IR/Instructions.h"
#include "llvm/IR/InstIterator.h"
#include "llvm/Analysis/AliasAnalysis.h"
#include "llvm/Analysis/MemoryLocation.h"
#include "llvm/Support/raw_ostream.h"
#include "llvm/Passes/PassBuilder.h"
#include "llvm/Passes/PassPlugin.h"

using namespace llvm;

namespace {

/// Convert ModRefInfo enum to readable text
static StringRef modRefInfoToStr(ModRefInfo MRI) {
  switch (MRI) {
    case ModRefInfo::NoModRef: return "NoModRef";
    case ModRefInfo::Ref:      return "Ref";
    case ModRefInfo::Mod:      return "Mod";
    case ModRefInfo::ModRef:   return "ModRef";
  }
  return "Unknown";
}

struct AAInspectorPass : public PassInfoMixin<AAInspectorPass> {
  PreservedAnalyses run(Function &F, FunctionAnalysisManager &AM) {
    errs() << "Function: " << F.getName()
           << " (" << F.getInstructionCount() << " instructions)\n";

    auto &AA = AM.getResult<AAManager>(F);
    bool AnyPrinted = false;

    //-----------------------------------------------------------------------
    // Alias results between all load/store instructions
    //-----------------------------------------------------------------------
    for (Instruction &I1 : instructions(F)) {
      MemoryLocation Loc1;
      if (auto *L = dyn_cast<LoadInst>(&I1))  Loc1 = MemoryLocation::get(L);
      if (auto *S = dyn_cast<StoreInst>(&I1)) Loc1 = MemoryLocation::get(S);
      if (!Loc1.Ptr) continue;

      for (Instruction &I2 : instructions(F)) {
        if (&I1 == &I2) continue;
        MemoryLocation Loc2;
        if (auto *L = dyn_cast<LoadInst>(&I2))  Loc2 = MemoryLocation::get(L);
        if (auto *S = dyn_cast<StoreInst>(&I2)) Loc2 = MemoryLocation::get(S);
        if (!Loc2.Ptr) continue;

        AliasResult R = AA.alias(Loc1, Loc2);
        if (R == AliasResult::NoAlias) continue; // skip trivial NoAlias to reduce noise

        errs() << "  Alias(" << *Loc1.Ptr << ", " << *Loc2.Ptr << ") = ";
        switch (R) {
          case AliasResult::NoAlias:      errs() << "NoAlias";      break;
          case AliasResult::MayAlias:     errs() << "MayAlias";     break;
          case AliasResult::PartialAlias: errs() << "PartialAlias"; break;
          case AliasResult::MustAlias:    errs() << "MustAlias";    break;
        }
        errs() << "\n";
        AnyPrinted = true;
      }
    }

    //-----------------------------------------------------------------------
    // Mod/Ref info for calls vs. memory operations
    //-----------------------------------------------------------------------
    for (Instruction &I : instructions(F)) {
      auto *CB = dyn_cast<CallBase>(&I);
      if (!CB || !CB->getCalledFunction()) continue;

      errs() << "  Call: " << CB->getCalledFunction()->getName() << "\n";

      for (Instruction &J : instructions(F)) {
        if (auto *SI = dyn_cast<StoreInst>(&J)) {
          ModRefInfo MRI = AA.getModRefInfo(CB, MemoryLocation::get(SI));
          errs() << "    vs store to " << *SI->getPointerOperand()
                 << " → " << modRefInfoToStr(MRI) << "\n";
          AnyPrinted = true;
        }
        if (auto *LI = dyn_cast<LoadInst>(&J)) {
          ModRefInfo MRI = AA.getModRefInfo(CB, MemoryLocation::get(LI));
          errs() << "    vs load from " << *LI->getPointerOperand()
                 << " → " << modRefInfoToStr(MRI) << "\n";
          AnyPrinted = true;
        }
      }
    }

    if (!AnyPrinted)
      errs() << "  (no aliasing or call memory interactions detected)\n";

    return PreservedAnalyses::all();
  }
};

} // namespace

// Register with the new PassManager
extern "C" LLVM_ATTRIBUTE_WEAK ::llvm::PassPluginLibraryInfo
llvmGetPassPluginInfo() {
  return {
    LLVM_PLUGIN_API_VERSION,
    "AAInspector",
    "v2.0",
    [](PassBuilder &PB) {
      PB.registerPipelineParsingCallback(
        [](StringRef Name, FunctionPassManager &FPM,
           ArrayRef<PassBuilder::PipelineElement>) {
          if (Name == "aa-inspector") {
            FPM.addPass(AAInspectorPass());
            return true;
          }
          return false;
        });
    }
  };
}

