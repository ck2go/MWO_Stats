import pytest
import os
import sys
import pandas as pd
import numpy as np

file_path = os.path.dirname(os.path.abspath(__file__))
package_path = os.path.abspath(os.path.join(file_path, '../'))
module_path = os.path.join(package_path, 'mwo_stats')
sys.path.append(module_path)

from mwo_stats import Match


class TestMatch1:

    def setup_class(self):
        match_filename = 'resources/test1.jpg'
        self.match = Match(match_filename)
        self.match.getStats()

    def teardown_class(self):
        del self.match
    
        
    def test_match1getStatsReturnsDf(self):
        assert type(self.match.getStats()) == pd.DataFrame
        
        
    def test_match1_correctMatchscores(self):
        control = np.array([429,169,143,99,416,347,309,167,398,353,257,193,463,260,97,69,416,304,155,126,565,162,75,47])
        df_test = self.match.getStats()
        test = np.array(df_test['matchscore'])
        print(control)
        print(test)
        print(control==test)
        assert np.all(test == control)
        
        
    def test_match1_correctDamages(self):
        control = np.array([768,276,194,60,634,442,424,291,579,474,351,276,733,327,157,96,400,446,254,141,1035,103,89,47])
        df_test = self.match.getStats()
        test = np.array(df_test['damage'])
        print(control)
        print(test)
        print(control==test)
        assert np.all(test == control)
        
        
    def test_match1_correctMechs(self):
        control = np.array(['MAD-4A(S)',
                            'DWF-B',
                            'MCII-DS',
                            'UM-K9',
                            'MLX-C',
                            'HSN-8P',
                            'BKL-A',
                            'PIR-3',
                            'MDD-B',
                            'SHC-P',
                            'HLF-1(S)',
                            'WHM-7S',
                            'MAD-IIC',
                            'BLR-2C',
                            'ACH-PRIME',
                            'CPLT-C1',
                            'KFX-PR',
                            'AWS-8Q',
                            'COU-E',
                            'UM-SC',
                            'KDK-3',
                            'NVA-S(C)',
                            'MDD-PRIME',
                            'MAL-1P'])
        df_test = self.match.getStats()
        test = np.array(df_test['mech'])
        print(control)
        print(test)
        print(control==test)
        assert np.all(test == control)
        
        
    def test_match1_correctPilots(self):
        control = np.array(['SHD2',
                            'Hunter Shock',
                            'TronTheOne',
                            'Boursemolle',
                            'Zonzelberg',
                            'Captainpeeweed',
                            'Sandokancio',
                            'Lanzers - Spain',
                            'Duxa',
                            'Boris the Tesla Trooper',
                            'Nicholas Hyde',
                            '-Havelock-',
                            'tizzk',
                            'goh4n',
                            'Wedjat',
                            'Billyum',
                            'Taifune',
                            'Nakedman',
                            'SocketWrench',
                            'grimm bastard',
                            'flep123',
                            'Kasegar',
                            '-XenoBeast-',
                            'ChronicAnger'])
        df_test = self.match.getStats()
        test = np.array(df_test['pilot'])
        print(control)
        print(test)
        print(control==test)
        assert np.all(test == control)

