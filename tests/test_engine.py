import importlib.util
import json
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('practice_engine',ROOT/'web/engine.py')
engine=importlib.util.module_from_spec(spec); spec.loader.exec_module(engine)
content=json.loads((ROOT/'web/content.json').read_text())
qs={q['id']:q for q in content['questions']}

class ContentTests(unittest.TestCase):
    def test_authored_counts_and_mapping(self):
        self.assertEqual(content['counts'],dict(short=30,debug=20,program=20,transfer=20,homework=10))
        self.assertEqual(len(qs),100)
        for mapping in content['mapping']:
            self.assertIn(mapping['homework'],qs)
            self.assertEqual(len(mapping['transfers']),2)
            for key in mapping['specials']+mapping['transfers']:
                self.assertIn(key,qs)
    def test_all_reference_programs(self):
        for q in content['questions']:
            with self.subTest(id=q['id']):
                if q['kind']=='short':
                    self.assertIn(q['solution'],range(len(q['choices'])))
                    self.assertTrue(q['explanation'])
                    continue
                result=engine.grade(q['solution'],q,q.get('solutionAlt',''))
                self.assertTrue(result['passed'],json.dumps(result,ensure_ascii=False))
                self.assertTrue(result['cases'])
    def test_all_debug_starters_fail(self):
        for q in content['questions']:
            if q['kind']=='debug':
                with self.subTest(id=q['id']): self.assertFalse(engine.grade(q['starter'],q)['passed'])
    def test_tiered_boundaries_reject_low_first(self):
        q=qs['H04']; bad=q['solution'].replace('if amount >= 1000:', 'if amount >= 200:')
        self.assertFalse(engine.grade(bad,q)['passed'])
        labels=[c['inputs'][0] for c in q['cases']]
        for value in ['199.99','200','200.01','499.99','500','500.01','999.99','1000','1000.01']:
            self.assertIn(value,labels)
    def test_quantity_boundary_and_percentage_rules(self):
        q=qs['H02']
        self.assertFalse(engine.grade(q['solution'].replace('n <= 5','n < 5'),q)['passed'])
        self.assertFalse(engine.grade(q['solution'].replace('Total cost less discount:', '10% off total:'),q)['passed'])
    def test_y_n_input_use(self):
        q=qs['H03']
        self.assertFalse(engine.grade('begin=input()\na=float(input())\nprint("Bye Bye")',q)['passed'])
    def test_converter_direction_and_invalid(self):
        q=qs['H06']
        self.assertFalse(engine.grade(q['solution'].replace('km / 1.60934','km * 1.60934'),q)['passed'])
        self.assertFalse(engine.grade(q['solution'].replace('print("This unit is invalid")','print("0.00 miles")'),q)['passed'])
    def test_days_duplicate_case_and_attempts(self):
        q=qs['H08']
        for old,new in [('range(7)','range(8)'),('day not in valid','day not in valid and day.title() not in valid'),('if day in entered:','if False:')]:
            with self.subTest(mutation=old): self.assertFalse(engine.grade(q['solution'].replace(old,new),q)['passed'])
    def test_times_two_implementations(self):
        q=qs['H10']
        self.assertFalse(engine.grade(q['solution'].replace('range(10, 0, -1)','range(10, 1, -1)'),q,q['solutionAlt'])['passed'])
        self.assertFalse(engine.grade(q['solution'],q,q['solution'])['passed'])
    def test_comments_and_dead_operations_not_structure(self):
        q=qs['P11']
        bad='# extend sort del\na=[1,2,5,8]\nif False:\n    a.extend([9]); a.sort()\nprint(a)'
        self.assertFalse(engine.grade(bad,q)['passed'])
    def test_movie_operations_are_same_object_and_ordered(self):
        q=qs['H07']
        bad='a=["a","b","c"]; a.extend(["d","e","f"]); a.sort()\nb=[1,2]; del b[0]\nprint(["a","b","c","d","e"])'
        self.assertFalse(engine.grade(bad,q)['passed'])
    def test_polygon_quantity_length_movement_and_overlap(self):
        q=qs['H09']
        for old,new in [('range(3, 13)','range(3, 12)'),('180 / n','180'),('t.penup()','t.pendown()'),('((n-3) % 5) * 120 - 260, ((n-3) // 5) * 140 - 100','0, 0')]:
            with self.subTest(mutation=old): self.assertFalse(engine.grade(q['solution'].replace(old,new),q)['passed'])
    def test_infinite_loop_limit(self):
        r=engine.execute('while True:\n    pass')
        self.assertEqual(r['error']['type'],'LimitError')
    def test_syntax_type_and_format_categories(self):
        self.assertEqual(engine.grade('if True\n print(2)',qs['P01'])['issues'][0]['category'],'语法错误')
        self.assertEqual(engine.grade('print(input()+2)',qs['P01'])['issues'][0]['category'],'类型错误')
        self.assertFalse(engine.grade('print("Price Qty Total $2.50 3 $7.50")',qs['P04'])['passed'])
    def test_zero_decimal_rounding(self):
        self.assertEqual(engine.execute('print(f"{2.8:.0f}")')['stdout'].strip(),'3')
    def test_function_definition_order(self):
        self.assertIsNone(engine.execute('def outer(): return inner()\ndef inner(): return 3\nprint(outer())')['error'])
        self.assertEqual(engine.execute('def outer(): return inner()\nprint(outer())\ndef inner(): return 3')['error']['type'],'NameError')
    def test_unused_functions_and_loops_rejected(self):
        self.assertFalse(engine.grade('def dummy(): return 0\ndummy()\nn=int(input())\nprint(f"{n*7.5:.2f}")',qs['P07'])['passed'])
        self.assertFalse(engine.grade('for i in range(2):\n    unrelated=1\nprint("3\\n6\\n9\\n12")',qs['P13'])['passed'])
    def test_print_cannot_replace_numeric_return(self):
        q=qs['P07']
        bad='def cost(n):\n    print(f"{n*7.5:.2f}")\ncost(int(input()))'
        self.assertFalse(engine.grade(bad,q)['passed'])
    def test_ignored_bool_result_cannot_check_days(self):
        q=qs['H08']
        bad=q['solution'].replace('if check_day(day, entered):','check_day(day, entered)\n    if day in ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"] and day not in entered:')
        self.assertFalse(engine.grade(bad,q)['passed'])
    def test_unrelated_list_operation_is_rejected(self):
        bad='b=[8,2]\nb.extend([5,1])\nb.sort()\na=[1,2,5,8]\nprint(a)'
        self.assertFalse(engine.grade(bad,qs['P11'])['passed'])

if __name__=='__main__': unittest.main()
