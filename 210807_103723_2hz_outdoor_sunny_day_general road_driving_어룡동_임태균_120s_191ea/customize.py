import numpy as np
import os
import io
import zipfile
import pickle
import glob
import json
from pathlib import Path
import xml.etree.ElementTree as ET

class NumpyEncoder(json.JSONEncoder):
    """ Special json encoder for numpy types """
    def default(self, obj):
        if isinstance(obj, (np.int_, np.int32)):
            return int(obj)
        elif isinstance(obj, (np.float_)):
            return float(obj)
        elif isinstance(obj, (np.ndarray,)):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)

def rename(frame):
    len_of_frame = len(frame)

    if len_of_frame>8:
        frame =  frame[:8]
    else:
        fill_zero = str(0) * (8 - len_of_frame)
        frame = fill_zero+frame
    return frame

def newfile(frame):
    dir_path = os.getcwd()
    base_name = os.path.basename(dir_path)
    for img_dir in glob.glob(f'{dir_path}/*Camera'):
        img_path = os.path.relpath(img_dir)
    vel_path = os.path.relpath('LiDAR')
    meta = base_name.split('_')
    new = {
        'image': {
            'image_idx': frame,
            'image_path': os.path.join(img_path,f'{frame}.jpg'),
            'image_shape': np.array([], dtype = np.int32),
            'meta_data': {
                'yymmdd' : meta[0],
                'hhmmss' : meta[1],
                'sr' : meta[2],
                'enviroment' : meta[3],
                'weather' : meta[4],
                'time':meta[5],
                'road_type':meta[6],
                'state' : meta[7],
                'place' : meta[8],
                'name' : meta[9],
                'length' : ' '.join(meta[10:])

            }
        },
        'point_cloud': {
            'num_features': 0,
            'velodyne_path': os.path.join(vel_path,f'{frame}.pcd')
        },
        'calib': {
            
        },              
        'annos': {
            'name': np.array([], dtype = '<U10'),
            'occluded': np.array([], dtype = np.int32),
            'alpha': np.array([]),
            'bbox': np.empty((0,4)),
            'polygon' : np.array([],dtype = '<U10'),
            'dimensions': np.empty((0,3)),
            'location': np.empty((0,3)),
            'rotation_y': np.array([]),
            'score': np.array([]),
            'index': np.array([], dtype = np.int32),
            'group_ids': np.array([], dtype = np.int32),
            'difficulty': np.array([], dtype = np.int32),
            'num_points_in_gt': np.array([], dtype = np.int32)
        }
    }
    if not os.path.exists('lable'):
        os.makedirs('lable')
    with open(f'lable/{frame}.pickle','wb') as f :
        pickle.dump(new, f)


def updatefile2(track, box, polygon, frame):
    with open(f'lable/{frame}.pickle','rb')as f :
        pkl_data = pickle.load(f)

    for data in box,polygon :
        if data is not None :
            pkl_data['annos']['name']=np.append(pkl_data['annos']['name'],track.attrib['label'])
            pkl_data['annos']['occluded']=np.append(pkl_data['annos']['occluded'],int(data.attrib['occluded']))
            pkl_data['annos']['alpha']=np.append(pkl_data['annos']['alpha'],np.nan)
            if data == box :
                pkl_data['annos']['bbox']=np.append(pkl_data['annos']['bbox'],np.array([[float(box.attrib['xtl']),float(box.attrib['ytl']),float(box.attrib['xbr']),float(box.attrib['ybr'])]]),axis=0)
                pkl_data['annos']['polygon']=np.append(pkl_data['annos']['polygon'],np.nan)
            else :
                pkl_data['annos']['bbox']=np.append(pkl_data['annos']['bbox'],np.array([[np.nan,np.nan,np.nan,np.nan]]),axis=0)
                pkl_data['annos']['polygon']=np.append(pkl_data['annos']['polygon'], polygon.attrib['points'])
            pkl_data['annos']['dimensions']=np.append(pkl_data['annos']['dimensions'], np.array([[np.nan,np.nan,np.nan]]),axis=0)
            pkl_data['annos']['location']=np.append(pkl_data['annos']['location'],np.array([[np.nan,np.nan,np.nan]]),axis=0)
            pkl_data['annos']['rotation_y']=np.append(pkl_data['annos']['rotation_y'],np.nan)
            pkl_data['annos']['score']=np.append(pkl_data['annos']['score'],np.nan)
            pkl_data['annos']['index']=np.append(pkl_data['annos']['index'],np.nan)
            pkl_data['annos']['group_ids']=np.append(pkl_data['annos']['group_ids'],np.nan)
            pkl_data['annos']['difficulty']=np.append(pkl_data['annos']['difficulty'],np.nan)
            pkl_data['annos']['num_points_in_gt']=np.append(pkl_data['annos']['num_points_in_gt'],np.nan)
        
    with open(f'lable/{frame}.pickle', 'wb') as make_file:
        pickle.dump(pkl_data, make_file)

            
def updatefile3(name,object, geometry):

    with open(f'lable/{name}.pickle','rb')as f :
        pkl_data = pickle.load(f)

    pkl_data['annos']['name']=np.append(pkl_data['annos']['name'],object['classTitle'])
    pkl_data['annos']['occluded']=np.append(pkl_data['annos']['occluded'],1 if object['tags'][0]['value']=='true' else 0)
    pkl_data['annos']['alpha']=np.append(pkl_data['annos']['alpha'],np.nan)
    pkl_data['annos']['bbox']=np.append(pkl_data['annos']['bbox'],np.array([[np.nan,np.nan,np.nan,np.nan]]),axis=0)
    pkl_data['annos']['polygon']=np.append(pkl_data['annos']['polygon'],np.nan)
    pkl_data['annos']['dimensions']=np.append(pkl_data['annos']['dimensions'], np.array([[geometry['dimensions']['x'],geometry['dimensions']['y'],geometry['dimensions']['z']]]),axis=0)
    pkl_data['annos']['location']=np.append(pkl_data['annos']['location'],np.array([[geometry['position']['x'],geometry['position']['y'],geometry['position']['z']]]),axis=0)
    pkl_data['annos']['rotation_y']=np.append(pkl_data['annos']['rotation_y'],geometry['rotation']['y'])
    pkl_data['annos']['score']=np.append(pkl_data['annos']['score'],np.nan)
    pkl_data['annos']['index']=np.append(pkl_data['annos']['index'],np.nan)
    pkl_data['annos']['group_ids']=np.append(pkl_data['annos']['group_ids'],np.nan)
    pkl_data['annos']['difficulty']=np.append(pkl_data['annos']['difficulty'],np.nan)
    pkl_data['annos']['num_points_in_gt']=np.append(pkl_data['annos']['num_points_in_gt'],np.nan)
    
    with open(f'lable/{name}.pickle', 'wb') as make_file:
        pickle.dump(pkl_data, make_file)

try:
    task_list = glob.glob('task*.zip')

    for task_zip in task_list :
        with zipfile.ZipFile(task_zip) as task :
            tlist = task.namelist()

            if 'annotations.xml' in tlist:
                with io.TextIOWrapper(task.open('annotations.xml', mode='r'), encoding='utf-8') as task_read :
                    xml_file = task_read.read()
                    root=ET.fromstring(xml_file)

                for task in root.iter('task'):
                    size = int(task.findtext('size'))

                for track in root.findall('track'):  
                    for i in range(0,size):
                        box = track.find(f'box[@frame="{i}"]')
                        polygon = track.find(f'polygon[@frame="{i}"]')
                        frame = None
                        if box is not None :
                            frame = rename(box.attrib['frame'])
                        elif polygon is not None :
                            frame = rename(polygon.attrib['frame'])
                        if frame :
                            if not os.path.isfile(f'lable/{frame}.pickle'):
                                newfile(frame)
                            updatefile2(track, box, polygon, frame)

        #3D 데이터 변환
            elif 'meta.json' in tlist :
                json_list = [j for j in tlist if 'ds0/ann/' in j]

                for json_file in json_list :
                    name=json_file[8:-9]
                    if not os.path.isfile(f'lable/{name}.pickle'):
                        newfile(name)

                    with io.TextIOWrapper(task.open(json_file, mode='r'), encoding='utf-8') as task_read :
                        json_data = json.load(task_read)

                        for object in json_data['objects'] :

                            for figure in json_data['figures']:
                                if figure['objectKey'] == object['key'] :
                                    updatefile3(name,object,figure['geometry'])


    #json 파일 생성
    pickle_list = glob.glob('lable/*.pickle')
    for pickle_file in pickle_list:
        with open(pickle_file, 'rb') as f:
            data = pickle.load(f)

        dumped = json.dumps(data, cls=NumpyEncoder,ensure_ascii=False)
        dumped=dumped.replace('NaN', 'null')

        base = os.path.basename(pickle_file)
        name,ext = os.path.splitext(base)

        with open(f'lable/{name}.json', 'a', encoding='utf-8') as f:
            f.write(dumped + '\n')

    print('완료')

except Exception as e :
    print(f'에러 발생 : {e}')

os.system('pause')
