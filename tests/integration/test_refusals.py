import pytest

OUT_OF_SCOPE = "outside my supported scope"


@pytest.mark.parametrize(
    "question",
    [
        "What's our total headcount in the Sales department?",
        "What's the weather in Durban?",
        "Who won the rugby?",
        "What is the depreciation on my laptops?",
        "asdf qwerty",
        "How many employees do we have?",
    ],
)
def test_questions_outside_the_data_are_refused(api, question):
    reply = api.ask(question)
    assert reply["scope"] == "out"
    assert OUT_OF_SCOPE in reply["answer"]


def test_headcount_points_to_hr_reporting(api):
    assert "Oracle or HR" in api.ask("What's our total headcount in the Sales department?")["answer"]


def test_unknown_location_is_refused_not_guessed(api):
    reply = api.ask("How many monitors are in Cape Town?")
    assert reply["scope"] == "out"
    assert "Cape Town" in reply["answer"]


def test_empty_question_is_rejected_by_the_api(api):
    import urllib.error
    import urllib.request

    request = urllib.request.Request(
        api.base_url + "/api/assistant/ask", b'{"question": "  "}', {"Content-Type": "application/json"}
    )
    with pytest.raises(urllib.error.HTTPError) as error:
        urllib.request.urlopen(request)
    assert error.value.code == 400
