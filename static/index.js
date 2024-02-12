// add event listener to submit event
document.getElementById('withdraw-form').addEventListener('submit', function(event) {
    event.preventDefault();

    var formData = new FormData(document.getElementById('withdraw-form'));

    fetch('/withdraw', {
        method: 'POST',
        body: formData
    })
    .then(response => response.text())
    .then(result => {
        document.getElementById('result').innerHTML = result;
    });
});