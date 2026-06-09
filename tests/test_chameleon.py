def test_demo_template_should_process_chameleon_vars(client):
    response = client.get("/")
    assert "<title>Demo</title>" in response.text


def test_demo_template_should_process_tal(client):
    response = client.get("/")
    assert "<p>Demo page text</p>" in response.text
