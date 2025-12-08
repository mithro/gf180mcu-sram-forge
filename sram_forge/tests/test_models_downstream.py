"""Tests for downstream repository models."""


from sram_forge.models.downstream import DownstreamRepo


def test_downstream_repo_from_dict():
    """DownstreamRepo can be created from dict."""
    data = {
        "name": "gf180mcu-ic-1x1-sram-u8b24k",
        "owner": "mithro",
        "sram": "u8b24k",
        "slot": "1x1",
        "config": "examples/sram_1x1_u8b24k.yaml",
        "deploy_key_secret": "DEPLOY_KEY_1X1",
    }
    repo = DownstreamRepo.model_validate(data)

    assert repo.name == "gf180mcu-ic-1x1-sram-u8b24k"
    assert repo.owner == "mithro"
    assert repo.sram == "u8b24k"
    assert repo.slot == "1x1"
    assert repo.config == "examples/sram_1x1_u8b24k.yaml"
    assert repo.deploy_key_secret == "DEPLOY_KEY_1X1"


def test_downstream_repo_full_name():
    """DownstreamRepo provides full GitHub repo name."""
    data = {
        "name": "gf180mcu-ic-1x1-sram-u8b24k",
        "owner": "mithro",
        "sram": "u8b24k",
        "slot": "1x1",
        "config": "examples/sram_1x1_u8b24k.yaml",
        "deploy_key_secret": "DEPLOY_KEY_1X1",
    }
    repo = DownstreamRepo.model_validate(data)

    assert repo.full_name == "mithro/gf180mcu-ic-1x1-sram-u8b24k"
