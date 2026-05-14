# Phase 9.5 Current Loop PI Suggestion

## Goal

Phase 9.5 connects the Mock identification workflow to loop tuning:

```text
Mock Rs + Mock Ld/Lq -> current-loop PI initial suggestion
```

This phase does not write parameters, does not connect hardware, and does not claim the suggested gains are final production gains.

## Implemented Service

`suggest_current_loop_pi` computes d/q current-loop PI initial values from:

- phase resistance `Rs`;
- d-axis inductance `Ld`;
- q-axis inductance `Lq`;
- target bandwidth.

The current first-order matching rule is:

```text
wc = 2 * pi * bandwidth
Kp = L * wc
Ki = R * wc
```

This is a reasonable initial teaching/engineering estimate, but real hardware still needs step-response and frequency-response validation.

## UI Integration

The 三环调参 page now contains a current-loop PI suggestion section:

- target bandwidth input;
- `生成 Mock PI 建议` button;
- Id/Iq PI suggestion table;
- update of the existing preset rows for d/q current loop.

The page clearly keeps the result as a suggestion. It does not write to `configs/parameters.json` or AxDr_L.

## Safety Boundary

Before these values can be written to real hardware, the following must exist:

- parameter write protocol;
- parameter range checks;
- motor stopped / safe state checks;
- voltage and current limit checks;
- step-response validation;
- manual confirmation;
- rollback to previous values.

## Next Steps

1. Add identification result export/report support.
2. Add mock current-loop step validation using the suggested PI values.
3. Add electrical-angle/phase-order Mock workflow.
4. Later connect suggestions to ParameterPage only through explicit review and write confirmation.
