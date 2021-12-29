import sys
import os
import pytesseract
import numpy as np
import cv2
import pandas as pd
from glob import glob

# ---------- CONSTANTS -------------
NUM_ROWS = 24
TEAM_SIZE = 12
LANCE_SIZE = 4
WHITE = 255


def loadImage(filename):
    img = cv2.imread(filename, cv2.IMREAD_GRAYSCALE)
    img = cv2.bitwise_not(img)
    
    img = cv2.resize(img, (2800, 1575), interpolation=cv2.INTER_LANCZOS4)
     
    img -= np.nanmin(img)
    img = img.astype(float)
    img /= np.nanmax(img)
    img *= WHITE
    img = img.astype(np.uint8)
    threshold = 220
    img[img > threshold] = WHITE

    x = 879
    y = 265
    h = 955
    w = 1494
    img_croped = img[y:y + h, x:x + w]
    return img_croped


def readColValues(img_col, mode='alphanum', debug=False):
    values = []
    spacing = 0
    for row in range(NUM_ROWS):
        if row > 0 and row % LANCE_SIZE == 0:
            spacing += 9
        if row == TEAM_SIZE:
            spacing += 7
            
        # cut out image
        start = row * (img_col.shape[0] // NUM_ROWS -1) + spacing
        stop = start + (img_col.shape[0] // NUM_ROWS -1) - 5
        im_tmp = img_col[start:stop, :]
        
        # blank first and last few lines and pad the image
        im_tmp[:2, :] = WHITE
        im_tmp[-5:, :] = WHITE
        im_tmp = np.pad(im_tmp, 4, 'constant', constant_values=WHITE)
        # im_tmp = cv2.resize(im_tmp, (int(im_tmp.shape[1]//0.7), int(im_tmp.shape[0]//0.7)), interpolation=cv2.INTER_LANCZOS4)
        custom_config = {'alphanum': '-c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ()- --psm 7',
                         'Pilot': '-c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz" "- --psm 7',
                         'digits': '-c tessedit_char_whitelist=0123456789 --psm 7'}[mode]
        text = pytesseract.image_to_string(im_tmp, config=custom_config).strip()
            
        if debug:
            print(f'{row}: {text}')
            print('-----')
            cv2.imshow("cropped", im_tmp)
            cv2.waitKey(0)
        values.append(text)
    
    return values


def getChassiAndVariant(mechs):
    known_mechs_file = os.path.join(os.path.dirname(sys.argv[0]),'mwo_chassis.csv')
    known_mechs = pd.read_csv(known_mechs_file)
    known_chassis = sorted(list(known_mechs['chassi']), key=len, reverse=True)
    
    chassis = []
    variants = []
    for mech in mechs:
        if mech[:mech.find('(')] in ('MAD-6S', 'MAD-4L','MAD-5A', 'MAD-4HP', 'MAD-4A', 'MAD-AL'):
            chassi = 'MAD2'
        else:
            found = False
            for chassi in known_chassis:
                if chassi == mech[:len(chassi)]:
                    found = True
                    break
            if not found:
                print(f'Unknown mech chassi for "{mech}"')
                chassi = input('Please enter the chassi name: ')
                print(f'got "{chassi}"')
                known_mechs = known_mechs.append({'chassi': chassi}, ignore_index=True)
                known_mechs.to_csv(known_mechs_file, index=False)
            
        chassis.append(chassi)
        if chassi == 'MAD2':
            variant = mech[len(chassi)-1:]
        else:
            variant = mech[len(chassi):]
        
        if len(variant)>0 and variant[0] == '-':
            variant = variant[1:]
        if '(' in variant:
            variant = variant[:variant.find('(')]
        variants.append(variant)
            
                
    return chassis, variants


# ========================== MAIN ==========================


def displayBestMechs(matches):
    best_mechs = matches[matches['matchscore']>350]
    print('----------------------------------------')
    print('BEST VARIANTS')
    print(best_mechs['mech'].value_counts())
    print('----------------------------------------')
    print('BEST CHASSIS')
    print(best_mechs['chassi'].value_counts())
    print('----------------------------------------')


if __name__ == '__main__':
    
    load_data = '' 
    datafile = 'matches.csv'
    
    if load_data:
        matches = pd.read_csv(datafile)
    else:
        columns = ['pilot', 'mech','chassi','variant','matchscore','damage']
        matches = pd.DataFrame(columns=columns)
            
        folder = '/home/koenig/tmp/old'
        
        filenames = glob(folder + '/*.jpg')
        for filename in filenames:
            print(f'Analyzing {filename}')
            img = loadImage(os.path.join(folder, filename))
            # cv2.imshow("cropped", img)
            # cv2.waitKey(0)
            
            # Pilot Column
            print('reading pilots...')
            x = 95
            width = 350
            img_col = img[:, x:x+width]
            pilots = readColValues(img_col, mode='Pilot', debug=False)
            
            
            # Damage Column
            print('reading damage...')
            x = 1335
            width = 80
            img_col = img[:, x:x+width]
            damage = np.asarray(readColValues(img_col, mode='digits', debug=False), dtype=int)
            
            
            # MatchScore Column
            print('reading matchscores...')
            x = 855
            width = 80
            img_col = img[:, x:x+width]
            matchscores = np.asarray(readColValues(img_col, mode='digits', debug=False), dtype=int)
            
            
            # Mech Column
            print('reading mechs...')
            x = 455
            width = 200
            img_col = img[:, x:x+width]
            mechs = readColValues(img_col, mode='alphanum', debug=False)
            print('  determining chassis and variants...')
            chassi, variant = getChassiAndVariant(mechs)
            
            print('done!')
            
            match = pd.DataFrame(list(zip(pilots, mechs, chassi, variant, matchscores, damage)), columns=columns)
            matches = matches.append(match)
                          
            print(matches)
            
        matches.to_csv(datafile, index=False)
        
    displayBestMechs(matches)
        
        