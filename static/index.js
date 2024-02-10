// add event listener to submit event
document.getElementById('deposit-form').addEventListener('submit', function(event) {
    event.preventDefault();

    var formData = new FormData(document.getElementById('deposit-form'));
    
    fetch('/deposit', {
        method: 'POST',
        body: formData
    })
    .then(response => response.text())
    .then(result => {
        document.getElementById('result').innerHTML = result;
    });
});