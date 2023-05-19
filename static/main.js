el = document.getElementById("notif");
el.setAttribute("style", "white-space: pre;");
document.getElementById("form1").onsubmit = function (e) {
    e.preventDefault();
    var fileInput = document.getElementById("C_file");
    var fileInput2 = document.getElementById("json_file");
    var formdata = new FormData();
    formdata.append("files", fileInput.files[0]);
    formdata.append("files", fileInput2.files[0]);

    var requestOptions = {
        method: "POST",
        body: formdata,
        redirect: "follow",
    };

    request = fetch("upload_files", requestOptions)
        .then((response) => {
            if (response.status == 200) {
                el.innerHTML = "Files uploaded successfully";
                n = fetch("test")
                    .then((response) => {
                        if (response.status == 200) {
                            response.json().then((data) => {
                                el.textContent = data["content"];
                                console.log(data["content"]);
                            });
                        } else {
                            el.innerHTML = "Testing failed";
                            console.log(response.body());
                        }
                    })
                    .catch((error) => console.log("error", error));
            } else {
                el.innerHTML = "File upload failed.";
                console.log(response.body());
            }
        })
        .catch((error) => console.log("error", error));
};
el2 = document.getElementById("notif2");
el2.setAttribute("style", "white-space: pre;");
document.getElementById("form2").onsubmit = function (e) {
    e.preventDefault();
    var fileInput = document.getElementById("tar_file");
    var formdata = new FormData();
    formdata.append("file", fileInput.files[0]);
    var requestOptions = {
        method: "POST",
        body: formdata,
        redirect: "follow",
    };
    request = fetch("untar", requestOptions)
        .then((response) => response.text())
        .then((result) => {
            el2.innerHTML = result;
        })
        .catch((error) => {
            el2.innerHTML = "Error: " + error;
            console.log("error", error);
        });
};
