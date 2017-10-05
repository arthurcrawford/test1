from raptly.pkg_util import prune


def test_prune():

    latest_pesto_version = 'Pamd64 pesto 9.32.1 58f826d62d1e9010'
    latest_caper_version = 'Pall caper 4.26.4-gamma 176826d62d1e9010'

    packages = ['Pall caper 4.25.3 3gh824d62d1e3010',
                'Pall caper 4.25.3 9ed826d62d1e3010',
                'Pall caper 4.25.4 9ed826d62d1e3010',
                'Pall caper 4.26.4 2c3826d62d1e9010',
                latest_caper_version,
                'Pall caper 4.26.4-beta 20c826d62d1e9010',
                'Pamd64 pesto 1 76a826d62d1e9010',
                'Pamd64 pesto 1.2.0 76a826d62d1e9010',
                'Pamd64 pesto 9.32.0 76a826d62d1e9010',
                latest_pesto_version]

    pruned = prune(packages)
    print(pruned)
    assert len(pruned) == 2
    assert latest_caper_version in pruned
    assert latest_pesto_version in pruned
