from sys import path
path.append("src/")


def test():
    from test_Data import test_Data
    from test_Song import test_Song
    from test_Parser import test_Parser
    from test_Playlists import test_Playlists
    from test_Query import test_Query

    tests = [
             (test_Song, "Song"),
             (test_Data, "Data"),
             (test_Playlists, "Playlists"),
             (test_Query, "Query"),
             (test_Parser, "Parser"),
            ]

    test_passed = 0
    for test, name in tests:
        try:
            test()
            print(f"✅ TEST {name} PASSED")
            test_passed += 1
        except Exception as e:
            print(f"❌ TEST {name} FAILD with '{e}'")
    if test_passed == len(tests):
        print("✅ ALL TESTS PASSED")
    else: 
        print(f"❌ {test_passed} OUT OF {len(tests)} PASSED")


if __name__ == "__main__":
    test()
