# XMLtoDict
- 본 프로그램은 지엔랩스의 Customize Datasets 가공 프로그램입니다.
- 현재 waveai의 디렉토리 구조는 아래 형식으로 이루어져있습니다.  
  일반도로 데이터  
  ├──2107  
  │   ├──210712  
  │   │   ├──210712_155529_10hz_outdoor_sunny_day_general road_driving_주행_이준수_506s_5069ea  
  │   │   │   ├──210713_144703_Camera  
  │   │   │   ├──AVM  
  │   │   │   ├──INS  
  │   │   │   ├──LiDAR  
  │   │   │   ├──RADAR  
  │   ├──210713  
  │   │   ├──210713_144703_10hz_outdoor_sunny_day_general road_driving_주행_이준수_205s_2042ea  
  │   │   ├──210713_151649_10hz_outdoor_sunny_day_general road_driving_주행_이준수_244s_2440ea  
  │   │   ├──210713_153310_10hz_outdoor_sunny_day_general road_driving_주행_이준수_40s_400ea  
  │   ├──210714  
  ├──2108  
  ├──2109  
  
- 210712_155529_10hz_outdoor_sunny_day_general road_driving_주행_이준수_506s_5069ea 단계의 폴더 안에 지엔랩스 내보내기 후 생성된 zip파일을 추가한 뒤 해당 프로그램을 실행하여주세요  
  ├──2107  
  │   ├──210712  
  │   │   ├──210712_155529_10hz_outdoor_sunny_day_general road_driving_주행_이준수_506s_5069ea  
  │   │   │   ├──210713_144703_Camera  
  │   │   │   ├──AVM  
  │   │   │   ├──INS  
  │   │   │   ├──LiDAR  
  │   │   │   ├──RADAR  
  **│   │   │   ├──task_test8_3d-2021_09_06_08_58_39-sly point cloud format 1.0.zip  
  │   │   │   ├──task_test8-2021_09_06_09_11_57-cvat for video 1.1.zip**
  
- ⭐ cutomize_top 프로그램 추가 : 상위 폴더에서 실행하면 하위 모든 파일의 데이터를 변환해줍니다.
  
