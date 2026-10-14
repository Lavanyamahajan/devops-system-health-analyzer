from python.log_analyzer import analyze_log


def test_log_counts(tmp_path):
    log = tmp_path / "app.log"
    log.write_text(
        "2026-10-14 09:00:00 INFO Started\n"
        "2026-10-14 09:01:00 ERROR Failed\n",
        encoding="utf-8",
    )

    result = analyze_log(str(log))

    assert result["total"] == 2
    assert result["levels"]["INFO"] == 1
    assert result["levels"]["ERROR"] == 1
    assert result["status"] == "WARNING"


def test_critical_log(tmp_path):
    log = tmp_path / "app.log"
    log.write_text(
        "2026-10-14 09:00:00 CRITICAL Service stopped\n",
        encoding="utf-8",
    )

    result = analyze_log(str(log))

    assert result["status"] == "CRITICAL"


def test_missing_log():
    result = analyze_log("missing_file.log")

    assert result["status"] == "CRITICAL"


def test_malformed_line(tmp_path):
    log = tmp_path / "app.log"
    log.write_text("This is not a valid log line\n", encoding="utf-8")

    result = analyze_log(str(log))

    assert result["malformed"] == 1
    assert result["total"] == 0
