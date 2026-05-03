from api_client import OpenF1Client
from feature_engineering import CornerDetector
from visualizer import TrackVisualizer

def main():
    #create instances of our classes
    api = OpenF1Client()
    detector = CornerDetector()
    viz = TrackVisualizer()

    # 2024 Silverstone Grand Prix, Lewis Hamilton
    session_key = 9558  # סילברסטון
    driver_number = 44  # המילטון

    print("Step 1: Downloading Telemetry...")
    df_tel = api.get_telemetry(session_key, driver_number)

    print("Step 2: Detecting Corners...")
    df_corners = detector.extract_corners(df_tel)
    print(f"Found {len(df_corners)} valid corners.")

    print("Step 3: Downloading Location Data...")
    df_loc = api.get_location(session_key, driver_number)

    print("Step 4: Drawing Track...")
    viz.draw_track_and_corners(df_corners, df_loc, driver_name="Lewis Hamilton")

if __name__ == "__main__":
    main()