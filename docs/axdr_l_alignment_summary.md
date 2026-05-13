# AxDr_L Alignment Summary

## Phase 2.5 Conclusion

AxDr_L is now the target firmware reference for eMotor-Studio. The repository was cloned into `external/target_firmware/AxDr_L`, and `external/` is ignored by git. No AxDr_L source code was copied into eMotor-Studio source directories.

The useful alignment target is the central PMSM runtime object `pm` and its nested fields:

- `pm.foc` for real-time signals.
- `pm.ctrl`, `pm.cmd`, and `pm.mode` for commands and control modes.
- `pm.para`, `pm.protect`, encoder structs, observer structs, and `pm.idpm` for parameter mapping.
- `pm.fault` for fault codes.

## Key Findings

- Main firmware entry is `AxDr_App/Core/Src/main.c`.
- Real control loop runs in `HAL_ADCEx_InjectedConvCpltCallback()` in `AxDr_App/User/motor/foc_ctrl.c`.
- Core type definitions live in `AxDr_App/User/motor/common.h`.
- Motor defaults and PI calculations live in `AxDr_App/User/motor/foc_drv.c`.
- Existing transport pieces include USB CDC, UART3, FDCAN1, and VOFA telemetry.
- No complete upper-computer command/parameter protocol was found.

## Phase 3-6 Adjustments

### Phase 3

- Generate `configs/signals.json` from `docs/axdr_l_signal_mapping.md`.
- Generate `configs/parameters.json` from `docs/axdr_l_parameter_mapping.md`.
- Generate `configs/fault_codes.json` from AxDr_L `pmsm_fault_t` bits.
- Generate `configs/commands.json` from `docs/axdr_l_protocol_plan.md`.
- Rewrite MockBackend behavior around AxDr_L-style fields: `bus_voltage`, `current_d`, `current_q`, `rotor_speed_filtered`, `mechanical_speed`, `speed_target_mechanical`, `run_state`, `system_mode`, `fault_word`.
- Dashboard should show AxDr_L signals first, not generic motor demo variables.

### Phase 4

- Scope channel list must come from `configs/signals.json`.
- ParameterPage must come from `configs/parameters.json`, grouped by AxDr_L concepts: Motor, Current Loop, Speed Loop, Position Loop, Limits, Protection, Encoder, Observer, Identification.
- CommandPage should use AxDr_L protocol command IDs and command names.

### Phase 5

- FaultPage should decode `pmsm_fault_t` bit names.
- Logger CSV columns should use signal names from `signals.json`.
- Report should mention AxDr_L commit and schema/config versions.

### Phase 6

- `BackendInterface` should match `docs/axdr_l_protocol_plan.md`.
- `SerialBackend` should be a TODO transport shell with AxDr_L frame hooks, not a real hardware implementation.
- Add provenance notes that AxDr_L is analyzed but not copied.

Phase 6 result:

- `SerialBackend` exists as a schema-aligned placeholder.
- Real serial/CAN communication remains intentionally unimplemented.
- Unsupported wire operations raise `ProtocolNotImplementedError`.
- Future V1.1 protocol work should fill `build_command_frame()`, `parse_telemetry_frame()`, command transport, parameter read/write, and telemetry stream handling.

## Configs To Create In Phase 3

Do not create these in Phase 2.5. Create them at Phase 3 start:

- `configs/signals.json`
- `configs/parameters.json`
- `configs/fault_codes.json`
- `configs/commands.json`

## Remaining Uncertainties

- Exact real-hardware serial protocol does not yet exist or was not located.
- Whether USB CDC, UART, or FDCAN should be the first V1.1 transport needs a hardware workflow decision.
- `pmsm_fault_check()` is present but commented out in the observed ADC callback.
- Some fault bits exist without complete located trigger logic.
- Some modes are declared but stubbed or not fully implemented.
- Safe parameter write rules need firmware-side confirmation before real hardware writes.
- Several comments are mojibake; symbol names and code flow were used as the main evidence.

## Recommendation

Proceed to Phase 3 only after accepting these mappings. Phase 3 should be an AxDr_L-aligned MockBackend and Dashboard phase, not a generic motor GUI phase.
