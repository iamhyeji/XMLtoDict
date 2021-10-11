import os
import io
import sys
import zipfile
import pickle
import glob
import json
import numpy as np
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
    frame = str(frame)
    len_of_frame = len(frame)

    if len_of_frame>8:
        frame =  frame[:8]
    else:
        fill_zero = str(0) * (8 - len_of_frame)
        frame = fill_zero+frame
    return frame

def newfile(frame,dir_path):

    base_name = os.path.basename(dir_path)
    img_path = os.path.relpath(f'{dir_path}/Camera')
    for img_dir in glob.glob(f'{dir_path}/*Camera'):
        img_path = os.path.relpath(img_dir)
    vel_path = os.path.relpath(f'{dir_path}/LiDAR')
    meta = base_name.split('_')
    if len(meta)<10:
        meta = ['' for i in range(10)]

    new = {
        'image': {
            'image_idx': frame,
            'image_path': os.path.join(img_path,f'{frame}.jpg'),
            'image_shape': np.array([], dtype = np.int32)
        },
        'point_cloud': {
            'num_features': 0,
            'velodyne_path': os.path.join(vel_path,f'{frame}.pcd')
        },
        "meta" : {
            'yymmdd' : meta[0],
            'hhmmss' : meta[1],
            'sr' : meta[2],
            'enviroment' : meta[3],
            'weather' : meta[4],
            'time':meta[5],
            'road_type':meta[6],
            'state' : meta[7],
            'place' : meta[-4],
            'name' : meta[-3],
            'length' : ' '.join(meta[10:])
        },
        'calib': {
            "intrinsic": np.array([
                [1.4355784e3, 0.0, 9.6e2],
                [0.0, 1.44520767e3, 5.4e2],
                [0.0, 0.0, 1.0]
            ], dtype=np.float),
            "dist": np.array([0.101923, -0.32098, 0.014438, 0.001353], dtype=np.float),
            "rot": np.array([[1.5372528], [-0.04260863], [0.02567258]], dtype=np.float),
            "tr": np.array([[0.03620099], [1.23389899], [1.35197656]], dtype=np.float),
            "extrinsic": np.array([
                [0.99898818, -0.04346468, -0.01155129],
                [-0.01009945, 0.03347534, -0.99938851],
                [0.04382479, 0.99849398, 0.0330025]
            ], dtype=np.float)           
        },              
        'annos': {
            'name': np.array([], dtype = '<U10'),
            'occluded': np.array([], dtype = np.int32),
            'parked': np.array([]),
            'bbox': np.empty((0,4)),
            'polygon' : np.array([],dtype = '<U10'),
            'smallcar': np.array([]),
            'pattern': np.array([]),
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
    if not os.path.exists(f'{path}/pickle'):
        os.makedirs(f'{path}/pickle')
    with open(f'{dir_path}/pickle/{frame}.pickle','wb') as f :
        pickle.dump(new, f)


def updatefile2(path,track, box, polygon, frame):
    with open(f'{path}/pickle/{frame}.pickle','rb')as f :
        pkl_data = pickle.load(f)

    for data in box,polygon :
        if data is not None and data.attrib['outside']=='0':
            pkl_data['annos']['name']=np.append(pkl_data['annos']['name'],track.attrib['label'])
            pkl_data['annos']['occluded']=np.append(pkl_data['annos']['occluded'],int(data.attrib['occluded']))
            if data == box :
                park_data = data.findtext('attribute[@name="주차"]')
                pkl_data['annos']['parked']=np.append(pkl_data['annos']['parked'],park_data if park_data is not None else np.nan )
                pkl_data['annos']['bbox']=np.append(pkl_data['annos']['bbox'],np.array([[float(box.attrib['xtl']),float(box.attrib['ytl']),float(box.attrib['xbr']),float(box.attrib['ybr'])]]),axis=0)
                pkl_data['annos']['polygon']=np.append(pkl_data['annos']['polygon'],np.nan)
                pkl_data['annos']['smallcar']=np.append(pkl_data['annos']['smallcar'],np.nan)
                pkl_data['annos']['pattern']=np.append(pkl_data['annos']['pattern'],np.nan)
            else :
                smallcar_data = data.findtext('attribute[@name="경차전용"]')
                pattern_data = data.findtext('attribute[@name="패턴"]')
                pkl_data['annos']['parked']=np.append(pkl_data['annos']['parked'],np.nan)
                pkl_data['annos']['bbox']=np.append(pkl_data['annos']['bbox'],np.array([[np.nan,np.nan,np.nan,np.nan]]),axis=0)
                pkl_data['annos']['polygon']=np.append(pkl_data['annos']['polygon'], polygon.attrib['points'])
                pkl_data['annos']['smallcar']=np.append(pkl_data['annos']['smallcar'],smallcar_data if smallcar_data is not None else np.nan )
                pkl_data['annos']['pattern']=np.append(pkl_data['annos']['pattern'],pattern_data if pattern_data is not None else np.nan)
            pkl_data['annos']['dimensions']=np.append(pkl_data['annos']['dimensions'], np.array([[np.nan,np.nan,np.nan]]),axis=0)
            pkl_data['annos']['location']=np.append(pkl_data['annos']['location'],np.array([[np.nan,np.nan,np.nan]]),axis=0)
            pkl_data['annos']['rotation_y']=np.append(pkl_data['annos']['rotation_y'],np.nan)
            pkl_data['annos']['score']=np.append(pkl_data['annos']['score'],np.nan)
            pkl_data['annos']['index']=np.append(pkl_data['annos']['index'],np.nan)
            pkl_data['annos']['group_ids']=np.append(pkl_data['annos']['group_ids'],np.nan)
            pkl_data['annos']['difficulty']=np.append(pkl_data['annos']['difficulty'],np.nan)
            pkl_data['annos']['num_points_in_gt']=np.append(pkl_data['annos']['num_points_in_gt'],np.nan)
        
    with open(f'{path}/pickle/{frame}.pickle', 'wb') as make_file:
        pickle.dump(pkl_data, make_file)

            
def updatefile3(path,name,object, geometry):

    with open(f'{path}/pickle/{name}.pickle','rb')as f :
        pkl_data = pickle.load(f)
    
    for tag in object['tags'] :
        if tag['name'] == 'occluded':
            oc = 1 if tag['value']=='true' else 0

    pkl_data['annos']['name']=np.append(pkl_data['annos']['name'],object['classTitle'])
    pkl_data['annos']['occluded']=np.append(pkl_data['annos']['occluded'],oc)
    pkl_data['annos']['parked']=np.append(pkl_data['annos']['parked'],np.nan)
    pkl_data['annos']['bbox']=np.append(pkl_data['annos']['bbox'],np.array([[np.nan,np.nan,np.nan,np.nan]]),axis=0)
    pkl_data['annos']['polygon']=np.append(pkl_data['annos']['polygon'],np.nan)
    pkl_data['annos']['dimensions']=np.append(pkl_data['annos']['dimensions'], np.array([[geometry['dimensions']['x'],geometry['dimensions']['y'],geometry['dimensions']['z']]]),axis=0)
    pkl_data['annos']['location']=np.append(pkl_data['annos']['location'],np.array([[geometry['position']['x'],geometry['position']['y'],geometry['position']['z']]]),axis=0)
    pkl_data['annos']['rotation_y']=np.append(pkl_data['annos']['rotation_y'],geometry['rotation']['z'])
    pkl_data['annos']['score']=np.append(pkl_data['annos']['score'],np.nan)
    pkl_data['annos']['index']=np.append(pkl_data['annos']['index'],np.nan)
    pkl_data['annos']['group_ids']=np.append(pkl_data['annos']['group_ids'],np.nan)
    pkl_data['annos']['difficulty']=np.append(pkl_data['annos']['difficulty'],np.nan)
    pkl_data['annos']['num_points_in_gt']=np.append(pkl_data['annos']['num_points_in_gt'],np.nan)
    
    with open(f'{path}/pickle/{name}.pickle', 'wb') as make_file:
        pickle.dump(pkl_data, make_file)

try:
    print('변환 중 ..')
    curr_path = os.path.dirname(sys.executable)   #exe파일생성시
    # curr_path = os.path.dirname(os.path.realpath(__file__))
    dir_list = ['*Camera','AVM','INS','LiDAR','RADAR','Vehicle']

    for (path,dir,files) in os.walk(curr_path):
        dir[:] = [d for d in dir if d not in dir_list]
        file_num = 0

        task_list = glob.glob(f'{path}/task*.zip')
        if task_list :
            task_list_2d= []
            task_list_3d=[]
            for task in task_list :
                if task.endswith('video 1.1.zip'):
                    task_list_2d.append(task)
                elif task.endswith('point cloud format 1.0.zip'):
                    task_list_3d.append(task)

            base_name = os.path.basename(path)
            # print(f'{base_name} 변환 중...')
            rel_name = os.path.relpath(path)
            file_num=0

            for filename in task_list_2d :

                with zipfile.ZipFile(filename) as task :

                    #2D 데이터 변환
                    with io.TextIOWrapper(task.open('annotations.xml', mode='r'), encoding='utf-8') as task_read :
                        xml_file = task_read.read()
                        root=ET.fromstring(xml_file)

                    for task in root.iter('task'):
                        size = int(task.findtext('size'))

                        for i in range(0,size):
                            newfile(rename(i+file_num),path)

                    for track in root.findall('track'):  
                        for i in range(0,size):
                            box = track.find(f'box[@frame="{i}"]')
                            polygon = track.find(f'polygon[@frame="{i}"]')
                            for data in box,polygon :
                                if data is not None :
                                    frame = rename(int(data.attrib['frame'])+file_num)
            
                                    if data.attrib['outside']=='0' :
                                        updatefile2(path,track, box, polygon, frame)
                    file_num += size
                        

                #3D 데이터 변환
            for filename in task_list_3d:
                with zipfile.ZipFile(filename) as task :
                    tlist = task.namelist()
                    json_list = [j for j in tlist if 'ds0/ann/' in j]

                    for json_file in json_list :
                        name=json_file[8:-9]
                        name = rename(int(name))
                        if not os.path.isfile(f'{path}/pickle/{name}.pickle'):
                            newfile(name,path)

                        with io.TextIOWrapper(task.open(json_file, mode='r'), encoding='utf-8') as task_read :
                            json_data = json.load(task_read)

                            for object in json_data['objects'] :
                                for figure in json_data['figures']:
                                    if figure['objectKey'] == object['key'] :
                                        updatefile3(path,name,object,figure['geometry'])
                # print(f'{base_name} 변환 완료')


        #json 파일 생성
        pickle_list = glob.glob(f'{path}/pickle/*.pickle')
        for pickle_file in pickle_list:
            with open(pickle_file, 'rb') as f:
                data = pickle.load(f)

            new_json = {
                "image": {
                    "image_path": data['image']['image_path']
                },

                "point_cloud": {
                    "velodyne_path": data['point_cloud']['velodyne_path']
                },
                "meta": {
                    "time": data['meta']['time'],
                    "enviroment": data['meta']['enviroment'],
                    "weather": data['meta']['weather'],
                    "place":data['meta']['place'],
                    "city": "Gwangju",
                    "terrain": "Urban",
                    "road_type": "",
                    "road_material": "Paved",
                    "parking_type1": "",
                    "parking_type2": "Normal"
                }
                ,
                "calib": {
                    "intrinsic": data['calib']['intrinsic'],
                    "dist": data['calib']['dist'],
                    "rot": data['calib']['rot'],
                    "tr": data['calib']['tr'],
                    "extrinsic": data['calib']['extrinsic'],
                },
                "bbox2d": [
                ],
                "segmentation": [
                ],
                "bbox3d": [
                    
                ]
            }

            for i,b in enumerate(data['annos']['bbox']):
                if not np.isnan(b).all() :
                    bbox2 = {
                        "name": ''.join([i for i in data['annos']['name'][i] if not i.isdigit()]),
                        "occluded": data['annos']['occluded'][i],
                        "bbox": b,
                    }
                    if data['annos']['parked'][i]!='nan':
                        bbox2["status"] = "Parked" if data['annos']['parked'][i]=='true' else "Not Parked"
                    new_json["bbox2d"].append(bbox2)

                elif data['annos']['polygon'][i] != 'nan' :
                    poly = data['annos']['polygon'][i].split(';')
                    polygons = []
                    for p in poly :
                        polygons.append([float(i) for i in p.split(',')])
                    segm = {
                        "name": ''.join([i for i in data['annos']['name'][i] if not i.isdigit()]),
                        "polygon": polygons,
                    }
                    if data['annos']['smallcar'][i]!='nan':
                        segm["size"] = "경차전용" if data['annos']['parked'][i]=='true' else "Nomal"
                    if data['annos']['pattern'][i]!='nan':
                        segm["pattern"] = data['annos']['pattern'][i] 

                    new_json['segmentation'].append(segm)
                
                elif not np.isnan(data['annos']['dimensions'][i]).all():
                    bbox3 ={
                        "name": ''.join([i for i in data['annos']['name'][i] if not i.isdigit()]),
                        "dimensions": data['annos']['dimensions'][i],
                        "location": data['annos']['location'][i],
                        "rotation_y": data['annos']['rotation_y'][i]
                    }

                    new_json['bbox3d'].append(bbox3)

            dumped = json.dumps(new_json, cls=NumpyEncoder,ensure_ascii=False, indent=4)
            import re
            dumped = re.sub('\[\s*(-?\d+.?\d+),?\s*\]', r'[ \1 ]', dumped)
            dumped = re.sub('\[\s*(-?\d+.?\d+),\s*(-?\d+.?\d+),?\s*\]', r'[ \1, \2 ]', dumped)
            dumped = re.sub('\[\s*(-?\d+.?\d+),\s*(-?\d+.?\d+),\s*(-?\d+.?\d+),?\s*\]', r'[ \1, \2 , \3 ]', dumped)
            dumped = re.sub('\[\s*(-?\d+.?\d+),\s*(-?\d+.?\d+),\s*(-?\d+.?\d+),\s*(-?\d+.?\d+),?\s*\]', r'[ \1, \2 , \3 , \4]', dumped)

            base = os.path.basename(pickle_file)
            name,ext = os.path.splitext(base)

            if not os.path.exists(f'{path}/label'):
                os.makedirs(f'{path}/label')
            
            with open(f'{path}/label/{name}.json', 'w', encoding='utf-8') as f:
                f.write(dumped)


    print('완료')

except Exception as e :
    print(f'에러 발생 : {e}')

os.system('pause')
