from emotor_studio.models import AxdrRunState, AxdrSystemMode, MotorMode, TelemetrySample


def test_telemetry_sample_contract() -> None:
    sample = TelemetrySample(
        timestamp=1.0,
        rpm=100.0,
        target_rpm=120.0,
        bus_voltage=48.0,
        phase_current=2.0,
        iq=1.4,
        id=0.1,
        temperature=35.0,
        power=69.0,
        mode=MotorMode.SPEED,
        faults=("MOCK",),
        signals={"current_q": 1.4, "run_state": "runing"},
        run_state=AxdrRunState.RUNNING,
        system_mode=AxdrSystemMode.RELEASE,
        fault_word=1,
    )

    assert sample.mode is MotorMode.SPEED
    assert sample.faults == ("MOCK",)
    assert sample.signals["current_q"] == 1.4
    assert sample.run_state is AxdrRunState.RUNNING
    assert sample.fault_word == 1
