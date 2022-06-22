function call_information(document.getElementById('all').textContent) {
fetch('call_all_info/' + getElementById('input')).then(response =>{
return response.json();
}).then(data =>{
console.log(data);
})
}
