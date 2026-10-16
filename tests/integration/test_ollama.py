"""The language model only picks a question type. Whatever it returns is validated before use."""


def test_model_choice_is_used_and_invented_values_are_dropped(fake_ollama):
    set_reply, make_api = fake_ollama
    set_reply(
        {
            "intent": "count_assets",
            "slots": {"asset_type": "Laptop", "status": "Available", "location": "Atlantis"},
        }
    )
    reply = make_api().ask("how many spare notebooks are there")
    assert reply["classifier"] == "ollama"
    assert reply["answer"].startswith("**3 laptops**")
    assert "Atlantis" not in str(reply)


def test_invented_question_type_is_refused(fake_ollama):
    set_reply, make_api = fake_ollama
    set_reply({"intent": "drop_all_tables", "slots": {}})
    assert make_api().ask("how many laptops?")["scope"] == "out"


def test_model_cannot_override_the_headcount_refusal(fake_ollama):
    set_reply, make_api = fake_ollama
    set_reply({"intent": "count_assets", "slots": {}})
    assert make_api().ask("What's our total headcount in the Sales department?")["scope"] == "out"


def test_rules_take_over_when_ollama_is_down(fake_ollama):
    _, make_api = fake_ollama
    reply = make_api("http://127.0.0.1:1").ask("How many laptops are available?")
    assert reply["classifier"] == "rules"
    assert reply["answer"].startswith("**3 laptops**")
