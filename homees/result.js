 
 window.addEventListener('load', () => {
    const params = (new URL(document.location)).searchParams;
    const address = params.get('name');
    document.getElementById('result_address').innerHTML = address;
    
    const base_url = 'https://orw1i0g55c.execute-api.us-east-1.amazonaws.com/Test/homees?address=';
    const new_url = base_url+address;

    fetch(new_url)
        .then((response) => {
            // The API call was successful!
            console.log("response:", response)
            return response.json();
    }).then((data) =>  {
            // This is the JSON from our response
        document.getElementById('log_error_score').innerHTML = Object.values(data)[0];
    }).catch(function (err) {
            // There was an error
        console.warn('Something went wrong.', err);
    });
 });
