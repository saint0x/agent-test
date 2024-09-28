import streamlit as st
import requests
import subprocess
import time
import sys
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Add the parent directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

API_PORT = 8080
API_URL = f"http://localhost:{API_PORT}"

def start_server():
    logging.info(f"Attempting to start test server on port {API_PORT}")
    try:
        env = os.environ.copy()
        env["PYTHONPATH"] = f"{parent_dir}:{env.get('PYTHONPATH', '')}"
        process = subprocess.Popen(
            ["uvicorn", "api-generation.test_imports:app", "--host", "0.0.0.0", f"--port", str(API_PORT)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=env
        )
        logging.info(f"Test server process started with PID {process.pid}")
        
        def log_output(pipe, log_func):
            for line in pipe:
                log_func(line.strip())
        
        import threading
        threading.Thread(target=log_output, args=(process.stdout, logging.info), daemon=True).start()
        threading.Thread(target=log_output, args=(process.stderr, logging.error), daemon=True).start()
        
        return process
    except Exception as e:
        logging.error(f"Failed to start test server: {str(e)}")
        return None

def stop_server(process):
    if process:
        logging.info(f"Stopping test server process with PID {process.pid}")
        process.terminate()
        process.wait()
        logging.info("Test server process stopped")
    else:
        logging.warning("Attempted to stop test server, but no process was found")

def check_server_status():
    logging.info("Checking test server status")
    try:
        response = requests.get(f"{API_URL}/")
        if response.status_code == 200:
            logging.info("Test server is running")
            return "running"
        else:
            logging.warning(f"Test server returned unexpected status code: {response.status_code}")
            return "error"
    except requests.ConnectionError:
        logging.info("Test server is not running")
        return "stopped"

def show_notification(message, emoji):
    if emoji in ["✅", "🚀", "🔑", "👤"]:
        st.success(f"{emoji} {message}")
    else:
        st.error(f"{emoji} {message}")
    logging.info(f"Notification: {emoji} {message}")

st.set_page_config(layout="wide")

st.title("Test API Frontend")

if 'server_process' not in st.session_state:
    st.session_state.server_process = None

if 'log_messages' not in st.session_state:
    st.session_state.log_messages = []

server_status = check_server_status()

col1, col2 = st.columns(2)

with col1:
    st.header("Controls")

    if st.button("Start Test Server"):
        if server_status != "running":
            st.session_state.server_process = start_server()
            if st.session_state.server_process:
                show_notification(f"Test server starting on port {API_PORT}...", "🚀")
                time.sleep(2)  # Give the server some time to start
                st.experimental_rerun()
            else:
                show_notification("Failed to start test server. Check logs for details.", "❌")
        else:
            show_notification("Test server is already running", "ℹ️")

    if st.button("Stop Test Server"):
        if server_status == "running":
            stop_server(st.session_state.server_process)
            st.session_state.server_process = None
            show_notification("Test server stopped", "🛑")
            time.sleep(1)  # Give the server some time to stop
            st.experimental_rerun()
        else:
            show_notification("Test server is not running", "ℹ️")

    st.subheader("Test Server Status")
    st.write(f"Status: {server_status}")
    st.write(f"API URL: {API_URL}")

with col2:
    st.header("Server Logs")
    log_output = st.empty()
    
    def update_logs():
        log_output.text("\n".join(st.session_state.log_messages[-50:]))  # Show last 50 log messages
    
    update_logs()

if __name__ == "__main__":
    logging.info("Test API Frontend is running. Use the controls on the left to interact with the test server.")
    st.write("Test API Frontend is running. Use the controls on the left to interact with the test server.")