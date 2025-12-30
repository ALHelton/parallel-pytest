import time

def test_addition():
    time.sleep(0.01)
    assert 1 + 1 == 2

def test_subtraction():
    time.sleep(0.01)
    assert 5 - 3 == 2

def test_multiplication():
    time.sleep(0.01)
    assert 3 * 4 == 12

def test_division():
    time.sleep(0.01)
    assert 10 / 2 == 5

def test_modulo():
    time.sleep(0.01)
    assert 10 % 3 == 1

def test_power():
    time.sleep(0.01)
    assert 2 ** 3 == 8

def test_floor_division():
    time.sleep(0.01)
    assert 10 // 3 == 3

def test_negative():
    time.sleep(0.01)
    assert -5 + 3 == -2

def test_abs():
    time.sleep(0.01)
    assert abs(-10) == 10

def test_max():
    time.sleep(0.01)
    assert max(1, 5, 3) == 5

def test_min():
    time.sleep(0.01)
    assert min(1, 5, 3) == 1

def test_sum():
    time.sleep(0.01)
    assert sum([1, 2, 3, 4]) == 10

def test_len():
    time.sleep(0.01)
    assert len([1, 2, 3]) == 3

def test_sorted():
    time.sleep(0.01)
    assert sorted([3, 1, 2]) == [1, 2, 3]

def test_reversed():
    time.sleep(0.01)
    assert list(reversed([1, 2, 3])) == [3, 2, 1]

def test_range():
    time.sleep(0.01)
    assert list(range(5)) == [0, 1, 2, 3, 4]

def test_enumerate():
    time.sleep(0.01)
    assert list(enumerate(['a', 'b'])) == [(0, 'a'), (1, 'b')]

def test_zip():
    time.sleep(0.01)
    assert list(zip([1, 2], ['a', 'b'])) == [(1, 'a'), (2, 'b')]

def test_map():
    time.sleep(0.01)
    assert list(map(lambda x: x * 2, [1, 2, 3])) == [2, 4, 6]

def test_filter():
    time.sleep(0.01)
    assert list(filter(lambda x: x > 2, [1, 2, 3, 4])) == [3, 4]

def test_all():
    time.sleep(0.01)
    assert all([True, True, True]) == True

def test_any():
    time.sleep(0.01)
    assert any([False, True, False]) == True

def test_bool():
    time.sleep(0.01)
    assert bool(1) == True

def test_int():
    time.sleep(0.01)
    assert int("42") == 42

def test_float():
    time.sleep(0.01)
    assert float("3.14") == 3.14

def test_str():
    time.sleep(0.01)
    assert str(42) == "42"

def test_list():
    time.sleep(0.01)
    assert list((1, 2, 3)) == [1, 2, 3]

def test_tuple():
    time.sleep(0.01)
    assert tuple([1, 2, 3]) == (1, 2, 3)

def test_set():
    time.sleep(0.01)
    assert set([1, 2, 2, 3]) == {1, 2, 3}

def test_dict():
    time.sleep(0.01)
    assert dict(a=1, b=2) == {'a': 1, 'b': 2}

def test_math_1():
    time.sleep(0.01)
    assert 100 + 50 == 150

def test_math_2():
    time.sleep(0.01)
    assert 200 - 75 == 125

def test_math_3():
    time.sleep(0.01)
    assert 25 * 4 == 100

def test_math_4():
    time.sleep(0.01)
    assert 100 / 4 == 25

def test_math_5():
    time.sleep(0.01)
    assert 17 % 5 == 2

def test_math_6():
    time.sleep(0.01)
    assert 3 ** 4 == 81

def test_math_7():
    time.sleep(0.01)
    assert 50 // 7 == 7

def test_math_8():
    time.sleep(0.01)
    assert -10 + 15 == 5

def test_math_9():
    time.sleep(0.01)
    assert abs(-25) == 25

def test_math_10():
    time.sleep(0.01)
    assert max(10, 20, 15) == 20

# def test_math_11_FAIL():
#     time.sleep(0.01)
#     assert 5 + 5 == 11  # Should be 10

def test_comparison_1():
    time.sleep(0.01)
    assert 5 > 3

def test_comparison_2():
    time.sleep(0.01)
    assert 10 >= 10

def test_comparison_3():
    time.sleep(0.01)
    assert 2 < 5

def test_comparison_4():
    time.sleep(0.01)
    assert 3 <= 3

def test_comparison_5():
    time.sleep(0.01)
    assert 5 == 5

def test_comparison_6():
    time.sleep(0.01)
    assert 5 != 6

def test_string_upper():
    time.sleep(0.01)
    assert "hello".upper() == "HELLO"

def test_string_lower():
    time.sleep(0.01)
    assert "WORLD".lower() == "world"

def test_string_capitalize():
    time.sleep(0.01)
    assert "test".capitalize() == "Test"

def test_string_title():
    time.sleep(0.01)
    assert "hello world".title() == "Hello World"

def test_string_strip():
    time.sleep(0.01)
    assert "  test  ".strip() == "test"

def test_string_split():
    time.sleep(0.01)
    assert "a,b,c".split(",") == ["a", "b", "c"]

def test_string_join():
    time.sleep(0.01)
    assert ",".join(["a", "b", "c"]) == "a,b,c"

def test_string_replace():
    time.sleep(0.01)
    assert "hello".replace("l", "x") == "hexxo"

def test_string_startswith():
    time.sleep(0.01)
    assert "hello".startswith("he") == True

def test_string_endswith():
    time.sleep(0.01)
    assert "hello".endswith("lo") == True

def test_string_find():
    time.sleep(0.01)
    assert "hello".find("l") == 2

def test_string_count():
    time.sleep(0.01)
    assert "hello".count("l") == 2

def test_string_isalpha():
    time.sleep(0.01)
    assert "hello".isalpha() == True

def test_string_isdigit():
    time.sleep(0.01)
    assert "123".isdigit() == True

def test_string_isalnum():
    time.sleep(0.01)
    assert "hello123".isalnum() == True

def test_list_append():
    time.sleep(0.01)
    lst = [1, 2]
    lst.append(3)
    assert lst == [1, 2, 3]

def test_list_extend():
    time.sleep(0.01)
    lst = [1, 2]
    lst.extend([3, 4])
    assert lst == [1, 2, 3, 4]

def test_list_insert():
    time.sleep(0.01)
    lst = [1, 3]
    lst.insert(1, 2)
    assert lst == [1, 2, 3]

def test_list_remove():
    time.sleep(0.01)
    lst = [1, 2, 3]
    lst.remove(2)
    assert lst == [1, 3]

def test_list_pop():
    time.sleep(0.01)
    lst = [1, 2, 3]
    assert lst.pop() == 3

def test_list_index():
    time.sleep(0.01)
    lst = [1, 2, 3]
    assert lst.index(2) == 1

def test_list_count():
    time.sleep(0.01)
    lst = [1, 2, 2, 3]
    assert lst.count(2) == 2

def test_list_sort():
    time.sleep(0.01)
    lst = [3, 1, 2]
    lst.sort()
    assert lst == [1, 2, 3]

def test_list_reverse():
    time.sleep(0.01)
    lst = [1, 2, 3]
    lst.reverse()
    assert lst == [3, 2, 1]

def test_list_clear():
    time.sleep(0.01)
    lst = [1, 2, 3]
    lst.clear()
    assert lst == []

def test_list_copy():
    time.sleep(0.01)
    lst = [1, 2, 3]
    copy = lst.copy()
    assert copy == [1, 2, 3]

# def test_list_slice_FAIL():
#     time.sleep(0.01)
#     lst = [1, 2, 3, 4, 5]
#     assert lst[1:3] == [2, 3, 4]  # Should be [2, 3]

def test_dict_get():
    time.sleep(0.01)
    d = {'a': 1}
    assert d.get('a') == 1

def test_dict_keys():
    time.sleep(0.01)
    d = {'a': 1, 'b': 2}
    assert list(d.keys()) == ['a', 'b']

def test_dict_values():
    time.sleep(0.01)
    d = {'a': 1, 'b': 2}
    assert list(d.values()) == [1, 2]

def test_dict_items():
    time.sleep(0.01)
    d = {'a': 1}
    assert list(d.items()) == [('a', 1)]

def test_dict_pop():
    time.sleep(0.01)
    d = {'a': 1, 'b': 2}
    assert d.pop('a') == 1

def test_dict_update():
    time.sleep(0.01)
    d = {'a': 1}
    d.update({'b': 2})
    assert d == {'a': 1, 'b': 2}

def test_dict_setdefault():
    time.sleep(0.01)
    d = {'a': 1}
    d.setdefault('b', 2)
    assert d == {'a': 1, 'b': 2}

def test_dict_clear():
    time.sleep(0.01)
    d = {'a': 1}
    d.clear()
    assert d == {}

def test_dict_copy():
    time.sleep(0.01)
    d = {'a': 1}
    copy = d.copy()
    assert copy == {'a': 1}

def test_set_add():
    time.sleep(0.01)
    s = {1, 2}
    s.add(3)
    assert s == {1, 2, 3}

def test_set_remove():
    time.sleep(0.01)
    s = {1, 2, 3}
    s.remove(2)
    assert s == {1, 3}

def test_set_union():
    time.sleep(0.01)
    assert {1, 2} | {2, 3} == {1, 2, 3}

def test_set_intersection():
    time.sleep(0.01)
    assert {1, 2, 3} & {2, 3, 4} == {2, 3}

def test_set_difference():
    time.sleep(0.01)
    assert {1, 2, 3} - {2, 3} == {1}