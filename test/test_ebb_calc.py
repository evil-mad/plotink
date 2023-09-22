"""
Tests for ebb_calc.py

part of https://github.com/evil-mad/plotink

"""

import unittest
# import copy
# import random
# import math

from plotink import ebb_calc

# python -m unittest discover in top-level package dir

# pylint: disable=too-many-public-methods



class EBBCalcTestCase(unittest.TestCase):
    """
    Unit tests for ebb_calc.py
    """

    def test_move_dist_lt(self):
        """ test move_dist_lt(rate, accel, time, accum) function """
        # Test cases are: [Rate, Accel, Time, Accumulator, Final pos, Final accum]
        test_cases = [
            [268435456,0,40,'clear',5,0],
            [490123456,0,22,'clear',5,45297792],
            [-490123456,0,22,'clear',-5,2102185855],
            [1073741824,0,2,'clear',1,0],
            [-1073741824,0,2,'clear',-1,2147483647],
            [490123456,0,20,1073741823,5,138792703],
            [-490123456,0,20,1073741823,-5,2008690943],
            [8589934,17353403,85,'clear',29,1142286978],
            [-8589934,-17353403,85,'clear',-29,1005196669],
            [8589934,17353403,83,2047483648,29,257219053],
            [-8589934,17353403,83,2047483648,28,978773657],
            [1800095000,-26012345,69,'clear',29,7141901],
            [-1800095000,26012345,69,'clear',-29,2140341746],
            [0,50353403,30,'clear',10,1184194885],
            [0,-50353403,30,'clear',-10,963288762],
            [1800095000,-54567890,69,'clear',-3,750143799],
            [-1800095000,54567890,69,'clear',3,1397339848],
            [10,-35111222,20,'clear',-3,1567690391],
            [-10,-35111222,20,'clear',-3,1567689991],
            [-10,35111222,20,'clear',3,579793256],
            [80000000,-35000000,19,'clear',-3,1644950944],
            [388300000,-35111222,27,'clear',-2,1981026877],
            [390000000,-35111222,27,'clear',-2,2026926877],
            [-390000000,35111222,27,'clear',2,120556770],
            [1204481500,-77012345,11,'clear',4,115030],
            [395851877,-77012345,17,115030,-3,2043764022],
            [1204481500,-77012345,11,'clear',4,115030],
            [-395851877,77012345,15,115030,1,578742047],
            [-1050109930,5099123,471,'clear',34,128535542],
            [-79000000,10015000,14,128535542,0,4005542],
            [-1050109930,5099123,471,'clear',34,128535542],
            [79000000,10015000,23,128535542,2,299535746],
            [-388686102,70433,8842,623903050,-318,21112357],
            [505377802,-143537,6884,1498912166,36,2140113428],
            [332897914,-30231,10818,1616956732,854,1825761],
            [540353247,-102800,367,'clear',89,260582377],
            [969802237,-278607,4419,29315105,728,1959708691],
            [978847345,-654,577969,455082516,212579,199874382],
            [978847345,-655,578247,455082516,212579,27378968],
            [978847345,-653,577692,455082516,212579,601512122],
            [1223372258,-217,7667213,1528960515,1397709,2145511894],
            [942132454,-175,2549531,'clear',853667,494970505],
            [1579676895,-2431086,651,27145044,238,2147356522],
            [-640499386,19406038,115,1979182198,26,809604235],
            [1135557706,-18994490,61,416382676,15,2133899377],
            [1833381763,0,2030,1657564855,1733,1833381761],
            [1833381763,0,2030,1657564856,1733,1833381762],
            [1833381763,0,2029,1657564857,1733,0],
            [1833381763,0,2029,1657564858,1733,1],
            [-1833381763,0,2030,489918792,-1733,314101886],
            [-1833381763,0,2030,489918791,-1733,314101885],
            [-1833381763,0,2029,489918790,-1733,2147483647],
            [268435456,0,40,0,5,0],
            [268435456,0,40,1,5,1],
            [268435456,0,40,2,5,2],
            [268435456,0,33,2147483647,5,268435455],
            [268435456,0,33,2147483646,5,268435454],
            [268435456,0,33,2147483645,5,268435453],
            [-490123456,0,18,0,-5,1915196032],
            [-490123456,0,18,1,-5,1915196033],
            [-490123456,0,18,2,-5,1915196034],
            [-490123456,0,22,2147483647,-5,2102185855],
            [-490123456,0,22,2147483646,-5,2102185854],
            [-490123456,0,22,2147483645,-5,2102185853],
            [1073741824,0,2,0,1,0],
            [1073741824,0,2,1,1,1],
            [1073741824,0,2,2,1,2],
            [1073741824,0,1,2147483647,1,1073741823],
            [1073741824,0,1,2147483646,1,1073741822],
            [1073741824,0,1,2147483645,1,1073741821],
            [-1073741824,0,1,0,-1,1073741824],
            [-1073741824,0,1,1,-1,1073741825],
            [-1073741824,0,1,2,-1,1073741826],
            [-1073741824,0,2,2147483647,-1,2147483647],
            [-1073741824,0,2,2147483646,-1,2147483646],
            [-1073741824,0,2,2147483645,-1,2147483645],
            [500000,-1000000,10,'clear',0,2102483647],
            [-500000,1000000,10,'clear',0,45000000],
            [500000,-1000000,1000,'clear',-232,863689983],
            [-500000,1000000,1000,'clear',232,1283793664],
            ]
        # Test cases are: [Rate, Accel, Time, Accumulator, Final pos, Final accum]

        for case in test_cases:
            pos_final, accum_final = ebb_calc.move_dist_lt(case[0], case[1], case[2], case[3])

            self.assertEqual(pos_final, case[4])
            self.assertEqual(accum_final, case[5])


    def test_move_dist_t3(self):
        """ test move_dist_t3(time, rate, accel, jerk, accum) function """
        test_cases = [
            [22,490123456,0,0,'clear',5,45297792],
            [22,-490123456,0,0,'clear',-5,2102185855],
            [2,1073741824,0,0,'clear',1,0],
            [2,-1073741824,0,0,'clear',-1,2147483647],
            [100,0,0,400000,'clear',31,94673512],
            [100,0,0,-400000,'clear',-31,2052810135],
            [19512,0,0,11,'clear',6341,1855618940],
            [19512,0,0,-11,'clear',-6341,291864707],
            [19512,-490123456,0,11,'clear',1889,1311430011],
            [19512,490123456,0,-11,'clear',-1889,836053636],
            [30000,0,-95000,11,'clear',3144,458869335],
            [30000,0,95000,-11,'clear',-3144,1688614312],
            [35000,-490123456,-125000,11,'clear',-7037,1335592123],
            [35000,490123456,125000,-11,'clear',7037,811891524],
            [35000,-490123456,-125000,11,2047483648,-7037,1235592124],
            [35000,490123456,125000,-11,2047483648,7038,711891524],
            [20,490123456,0,0,1073741823,5,138792703],
            [20,-490123456,0,0,1073741823,-5,2008690943],
            [85,8589934,17353403,0,'clear',29,1142286978],
            [85,-8589934,-17353403,0,'clear',-29,1005196669],
            [83,8589934,17353403,0,2047483648,29,257219053],
            [83,-8589934,17353403,0,2047483648,28,978773657],
            [22,490123456,0,100000,'clear',5,222764444],
            [22,-490123456,0,100000,'clear',-4,132168859],
            [22,490123456,0,-100000,'clear',4,2015314788],
            [22,-490123456,0,-100000,'clear',-5,1924719203],
            [69,1800095000,-26012345,600999,'clear',44,700483895],
            [69,-1800095000,26012345,-600999,'clear',-44,1446999752],
            [30,0,50353403,0,'clear',10,1184194885],
            [30,0,-50353403,0,'clear',-10,963288762],
            [30,0,50353403,100,'clear',10,1184644865],
            [30,0,-50353403,100,'clear',-10,963738742],
            [20,10,-35111222,0,'clear',-3,1567690391],
            [20,-10,-35111222,0,'clear',-3,1567689991],
            [20,-10,35111222,0,'clear',3,579793256],
            [20,18000000,0,-3600000,'clear',-3,2002450944],
            [20,-18000000,0,3600000,'clear',3,145032703],
            [20,478000000,0,-9600000,'clear',-2,1054967296],
            [20,-478000000,0,9600000,'clear',2,1092516351],
            [3338,225,-513,-38,'clear',-111,2106467160],
            [3338,-225,513,38,'clear',111,41016487],
            [2623,254,-563,173,'clear',242,863356844],
            [2623,-254,563,-173,'clear',-242,1284126803],
            [3000,100,-300,300,'clear',628,30569056],
            [3000,-100,300,-300,'clear',-628,2116914591],
            [3000,100,-300,300,'clear',628,30569056],
            [3000,-100,300,-300,'clear',-628,2116914591],
            [1000,500000,-1000000,0,'clear',-232,863689983],
            [1000,-500000,1000000,0,'clear',232,1283793664],
            [1000,500000,-1000000,5,'clear',-232,1697022483],
            [1000,-500000,1000000,-5,'clear',232,450461164],
            [372,2147054151,-1171655,3481,'clear',348,176993308],
            ]
        # Test cases are: [Time, Rate, Accel, Jerk, Accumulator, Final pos, Final accum]

        for case in test_cases:
            pos_final, accum_final =\
                ebb_calc.move_dist_t3(case[0], case[1], case[2], case[3], case[4])

            self.assertEqual(pos_final, case[5])
            self.assertEqual(accum_final, case[6])

            print(f"    Expected final position X={pos_final}")
            print(f"    Expected Final C={accum_final}")



    def test_rate_t3(self):
        """ test rate_t3(time, rate, accel, jerk) function """
        test_cases = [
            [22,490123456,0,0,490123456],
            [22,-490123456,0,0,-490123456],
            [2,1073741824,0,0,1073741824],
            [2,-1073741824,0,0,-1073741824],
            [100,0,0,400000,1980066666],
            [100,0,0,-400000,-1980066666],
            [19512,0,0,11,2093842477],
            [19512,0,0,-11,-2093842477],
            [19512,-490123456,0,11,1603719021],
            [19512,490123456,0,-11,-1603719021],
            [30000,0,-95000,11,2099882501],
            [30000,0,95000,-11,-2099882501],
            [35000,-490123456,-125000,11,1872246545],
            [35000,490123456,125000,-11,-1872246545],
            [35000,-490123456,-125000,11,1872246545],
            [35000,490123456,125000,-11,-1872246545],
            [20,490123456,0,0,490123456],
            [20,-490123456,0,0,-490123456],
            [85,8589934,17353403,0,1474952488],
            [85,-8589934,-17353403,0,-1474952488],
            [83,8589934,17353403,0,1440245682],
            [83,-8589934,17353403,0,1423065814],
            [22,490123456,0,100000,513240122],
            [22,-490123456,0,100000,-467006790],
            [22,490123456,0,-100000,467006790],
            [22,-490123456,0,-100000,-513240122],
            [69,1800095000,-26012345,600999,1428293187],
            [69,-1800095000,26012345,-600999,-1428293187],
            [30,0,50353403,0,1485425389],
            [30,0,-50353403,0,-1485425389],
            [30,0,50353403,100,1485468905],
            [30,0,-50353403,100,-1485381873],
            [20,10,-35111222,0,-684668819],
            [20,-10,-35111222,0,-684668839],
            [20,-10,35111222,0,684668819],
            [20,18000000,0,-3600000,-666600000],
            [20,-18000000,0,3600000,666600000],
            [20,478000000,0,-9600000,-1347600000],
            [20,-478000000,0,9600000,1347600000],
            [3338,225,-513,-38,-213351133],
            [3338,-225,513,38,213351133],
            [2623,254,-563,173,593428083],
            [2623,-254,563,-173,-593428083],
            [3000,100,-300,300,1348650300],
            [3000,-100,300,-300,-1348650300],
            [3000,100,-300,300,1348650300],
            [3000,-100,300,-300,-1348650300],
            [1000,500000,-1000000,0,-999000000],
            [1000,-500000,1000000,0,999000000],
            [1000,500000,-1000000,5,-996502500],
            [1000,-500000,1000000,-5,996502500],
            [372,2147054151,-1171655,3481,1951994784],
            ]
        # Test cases are: [Time, Rate, Accel, Jerk, Final Rate]

        for case in test_cases:
            final_rate = ebb_calc.rate_t3(case[0], case[1], case[2], case[3])
            self.assertEqual(final_rate, case[4])



    def test_calculate_lm(self):
        """ test calculate_lm(steps, rate, accel, accum) function """
        # Test cases are: [Steps, Rate, Accel, Accumulator, Final time, Final pos, Final accum]
        test_cases = [
            [5,268435456,0,'clear',40,5,0],
            [5,-268435456,0,'clear',40,-5,2147483647],
            [5,490123456,0,'clear',22,5,45297792],
            [5,-490123456,0,'clear',22,-5,2102185855],
            [1,1073741824,0,'clear',2,1,0],
            [1,-1073741824,0,'clear',2,-1,2147483647],
            [5,490123456,0,1073741823,20,5,138792703],
            [5,-490123456,0,1073741823,20,-5,2008690943],
            [29,8589934,17353403,'clear',85,29,1142286978],
            [29,-8589934,-17353403,'clear',85,-29,1005196669],
            [29,8589934,17353403,2047483648,83,29,257219053],
            [29,-8589934,17353403,2047483648,84,29,271709226],
            [29,1800095000,-26012345,'clear',69,29,7141901],
            [29,-1800095000,26012345,'clear',69,-29,2140341746],
            [10,0,50353403,'clear',30,10,1184194885],
            [10,0,-50353403,'clear',30,-10,963288762],
            [29,1800095000,-54567890,'clear',69,-3,750143799],
            [29,-1800095000,54567890,'clear',69,3,1397339848],
            [3,10,-35111222,'clear',20,-3,1567690391],
            [3,-10,-35111222,'clear',20,-3,1567689991],
            [3,-10,35111222,'clear',20,3,579793256],
            [3,80000000,-35000000,'clear',19,-3,1644950944],
            [2,388300000,-35111222,'clear',27,-2,1981026877],
            [4,390000000,-35111222,'clear',27,-2,2026926877],
            [4,-390000000,35111222,'clear',27,2,120556770],
            [4,1204481500,-77012345,'clear',11,4,115030],
            [3,395851877,-77012345,115030,17,-3,2043764022],
            [4,1204481500,-77012345,'clear',11,4,115030],
            [3,-395851877,77012345,115030,15,1,578742047],
            [134,-1050109930,5099123,'clear',471,34,128535542],
            [2,-79000000,10015000,128535542,14,0,4005542],
            [134,-1050109930,5099123,'clear',471,34,128535542],
            [2,79000000,10015000,128535542,23,2,299535746],
            [682,-388686102,70433,623903050,8842,-318,21112357],
            [792,505377802,-143537,1498912166,6884,36,2140113428],
            [854,332897914,-30231,1616956732,10818,854,1825761],
            [89,540353247,-102800,'clear',367,89,260582377],
            [842,969802237,-278607,29315105,4419,728,1959708691],
            [212579,978847345,-654,455082516,577969,212579,199874382],
            [212579,978847345,-655,455082516,578247,212579,27378968],
            [212579,978847345,-653,455082516,577692,212579,601512122],
            [1813937,1223372258,-217,1528960515,7667213,1397709,2145511894],
            [853667,942132454,-175,'clear',2549531,853667,494970505],
            [240,1579676895,-2431086,27145044,651,238,2147356522],
            [36,-640499386,19406038,1979182198,115,26,809604235],
            [17,1135557706,-18994490,416382676,61,15,2133899377],
            [1733,1833381763,0,1657564855,2030,1733,1833381761],
            [1733,1833381763,0,1657564856,2030,1733,1833381762],
            [1733,1833381763,0,1657564857,2029,1733,0],
            [1733,1833381763,0,1657564858,2029,1733,1],
            [1733,-1833381763,0,489918792,2030,-1733,314101886],
            [1733,-1833381763,0,489918791,2030,-1733,314101885],
            [1733,-1833381763,0,489918790,2029,-1733,2147483647],
            [5,268435456,0,0,40,5,0],
            [5,268435456,0,1,40,5,1],
            [5,268435456,0,2,40,5,2],
            [5,268435456,0,2147483647,33,5,268435455],
            [5,268435456,0,2147483646,33,5,268435454],
            [5,268435456,0,2147483645,33,5,268435453],
            [5,-490123456,0,0,18,-5,1915196032],
            [5,-490123456,0,1,18,-5,1915196033],
            [5,-490123456,0,2,18,-5,1915196034],
            [5,-490123456,0,2147483647,22,-5,2102185855],
            [5,-490123456,0,2147483646,22,-5,2102185854],
            [5,-490123456,0,2147483645,22,-5,2102185853],
            [1,1073741824,0,0,2,1,0],
            [1,1073741824,0,1,2,1,1],
            [1,1073741824,0,2,2,1,2],
            [1,1073741824,0,2147483647,1,1,1073741823],
            [1,1073741824,0,2147483646,1,1,1073741822],
            [1,1073741824,0,2147483645,1,1,1073741821],
            [1,-1073741824,0,0,1,-1,1073741824],
            [1,-1073741824,0,1,1,-1,1073741825],
            [1,-1073741824,0,2,1,-1,1073741826],
            [1,-1073741824,0,2147483647,2,-1,2147483647],
            [1,-1073741824,0,2147483646,2,-1,2147483646],
            [1,-1073741824,0,2147483645,2,-1,2147483645],
            [1,500000,-1000000,'clear',67,-1,2083967295],
            [1,-500000,1000000,'clear',67,1,63516352],
        ]
        # Test cases are: [Steps, Rate, Accel, Accumulator, Final time, Final pos, Final accum]

        for case in test_cases:
            move_time, pos_final, accum_final =\
                ebb_calc.calculate_lm(case[0], case[1], case[2], case[3])

            self.assertEqual(move_time, case[4])
            self.assertEqual(pos_final, case[5])
            self.assertEqual(accum_final, case[6])
