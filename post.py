import requests

# Define the URL of the web server
url = 'http://localhost:5000/post_endpoint'  # Adjust port and endpoint as needed

# Define the data to be sent
data = {
    'timestamp': '11/11/2023T11:01:04',
    'values': '1.63, 2.13, 84.74, 5.65, 93.48, 1.97, 362.32'
}

try:
    # Send POST request with the data
    response = requests.post(url, data=data)

    # Check the response
    if response.status_code == 200:
        print("Data sent successfully!")
    else:
        print("Error:", response.status_code)

except Exception as e:
    print("An error occurred:", e)
