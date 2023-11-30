import concurrent.futures
import subprocess


def run_flask_app():
    subprocess.run(["python", "run.py"])


def run_streamlit_app():
    subprocess.run(["streamlit", "run", "streamApp.py"])


if __name__ == "__main__":
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # Start the Flask app in one thread
        flask_future = executor.submit(run_flask_app)

        # Start the Streamlit app in another thread
        streamlit_future = executor.submit(run_streamlit_app)

        # Wait for both threads to complete
        concurrent.futures.wait([flask_future, streamlit_future])
