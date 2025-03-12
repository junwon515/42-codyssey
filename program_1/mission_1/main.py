from pathlib import Path
import csv
import json

print('\nHello Mars')

# 파일 경로 설정
parent_path = Path(__file__).parent
main_log_path = parent_path / 'mission_computer_main.log'
log_analysis_path = parent_path / 'log_analysis.md'
error_log_path = parent_path / 'mission_computer_error.log'
json_log_path = parent_path / 'mission_computer_main.json'

# 로그 분석 보고서 내용
log_analysis_content = """# Rocket Launch Incident Analysis Report

## Incident Summary
On **August 27, 2023**, a rocket was successfully launched and completed its mission objectives, including satellite deployment and reentry maneuvers. However, a critical incident occurred at **11:35 AM**, involving an **oxygen tank instability**, which subsequently led to an **oxygen tank explosion** at **11:40 AM**.

## Timeline of Events

### Pre-Launch and Launch Phase
- **10:00 AM - 10:30 AM**: Rocket systems initialized, checked, and launched successfully.
- **10:32 AM - 11:00 AM**: Rocket ascended, passed Max-Q, completed stage separations, and entered orbit.
- **11:05 AM**: Satellite deployment was confirmed successful.

### Reentry and Landing Phase
- **11:10 AM**: Deorbit maneuvers initiated.
- **11:15 AM**: Reentry sequence started with atmospheric drag detected.
- **11:20 AM**: Heat shield functioning as expected.
- **11:25 AM**: Main parachutes deployed, slowing descent.
- **11:28 AM**: Rocket touchdown confirmed.

### Incident Details
- **11:35 AM**: **Oxygen tank instability detected.**
- **11:40 AM**: **Oxygen tank explosion occurred.**
- **12:00 PM**: Mission control and center systems powered down.

## Analysis of the Incident
The oxygen tank instability reported at **11:35 AM** suggests a structural or pressure anomaly within the tank. This instability rapidly escalated into an explosion within five minutes, indicating a probable overpressure scenario, material failure, or a compromised valve system.

### Possible Causes
1. **Thermal Stress from Reentry:**
   - The reentry phase (starting at **11:15 AM**) subjected the rocket to extreme heat and pressure changes.
   - If the oxygen tank was not adequately insulated, this could have led to internal pressure buildup.

2. **Structural Fatigue or Manufacturing Defect:**
   - Extended exposure to vibrations during ascent and descent could have weakened tank integrity.
   - A pre-existing flaw in the tank material or welds might have worsened under stress.

3. **Valve or Pressure Regulator Malfunction:**
   - Improper venting of excess pressure could have caused an uncontrollable pressure increase.
   - If the relief valve failed, the tank would have remained sealed under extreme pressure.

## Recommendations for Future Missions
1. **Enhanced Thermal Protection:**
   - Improve insulation and shielding for cryogenic tanks to withstand reentry conditions.
2. **Structural Integrity Tests:**
   - Conduct more rigorous material fatigue and vibration testing before launch.
3. **Redundant Pressure Regulation Systems:**
   - Implement dual safety valves to prevent overpressure incidents.
4. **Post-Landing Diagnostics:**
   - Install real-time telemetry for tank pressure readings post-touchdown to detect abnormalities early.

## Conclusion
The mission was largely successful, but the **oxygen tank explosion** post-landing is a critical issue that requires further investigation. Implementing the above recommendations will enhance safety and prevent similar incidents in future missions.

---
**Report Prepared by:** Dr. Songhee Han  
**Date:** August 27, 2023
"""

try:
    # 로그 파일 읽기
    with main_log_path.open('r', encoding='utf-8') as log_file:
        log_lines = log_file.readlines()

    # 로그 전체 출력
    print('\n=== Log Output ===')
    print(''.join(log_lines))

    # 로그 역순 출력
    print('\n=== Log Output (Reversed) ===')
    print(''.join(reversed(log_lines)))

    # 문제가 되는 로그 저장
    with error_log_path.open('w', encoding='utf-8') as core_log_file:
        core_log_file.writelines(log_lines[-3:])

    # 로그 분석 보고서 저장
    with log_analysis_path.open('w', encoding='utf-8') as log_analysis_file:
        log_analysis_file.write(log_analysis_content)

    print('\n✅ Processing completed successfully!')


    # 로그 CSV 파싱
    logs = []
    with main_log_path.open('r', encoding='utf-8') as log_file:
        reader = csv.reader(log_file, delimiter=',')
        headers = next(reader, None)
        logs = [row for row in reader]

    # 로그 리스트 출력
    print('\n=== Log list ===')
    print(logs)

    # 로그 시간 역순 정렬
    sorted_logs = sorted(logs, key=lambda x: x[0], reverse=True)

    # 로그 사전 객체로 변환
    log_dict = [dict(zip(headers, log)) for log in sorted_logs]

    # 로그 사전 json 파일로 저장
    with json_log_path.open('w', encoding='utf-8') as json_file:
        json.dump(log_dict, json_file, indent=4)

    print('\n✅ JSON file created successfully!')

except (FileNotFoundError, IOError, PermissionError) as e:
    print(f'❌ Error: {e}')
except Exception as e:
    print(f'❌ An unexpected error occurred: {e}')
