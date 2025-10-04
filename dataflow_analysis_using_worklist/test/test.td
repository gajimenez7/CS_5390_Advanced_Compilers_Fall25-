@test call.bril
@expect call.json
@run { bash -c "bril2json" < call.bril }
