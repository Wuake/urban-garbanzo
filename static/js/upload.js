class FileUpload {

    progress = document.getElementById("progress");
    progress_wrapper = document.getElementById("progress_wrapper");
    progress_status = document.getElementById("progress_status");

    upload_btn = document.getElementById("upload_btn");
    loading_btn = document.getElementById("loading_btn");
    cancel_btn = document.getElementById("cancel_btn");

    //id de la présentation pour enregistrer au bon endroit
    // id_presta = document.getElementById("btn_fichier").attributes["value_presta"].value;  
    
    xhrajax;
    aborted = 0;
    constructor(input) {
        this.input = input
        this.max_length = 1024 * 1024 * 1000; // * 1GB de taille max
    }

    create_progress_bar() {
        progress_wrapper.innerHTML  = `
            <small class="textbox"> -- </small>
            <div class="progress" style="margin-top: 5px;">
                <div class="progress-bar bg-success" role="progressbar" aria-valuenow="0" aria-valuemin="0" aria-valuemax="100" style="width: 0%">  </div>
            </div>`
    }

    reset() {
        this.input.value = null;
        cancel_btn.classList.add("d-none");
        this.input.disabled = false;
        upload_btn.classList.remove("d-none");
        loading_btn.classList.add("d-none");
        progress_wrapper.classList.add("d-none");
        alert_wrapper.classList.remove("d-none");        
    }

    show_alert(message, alert) {
        alert_wrapper.innerHTML = `
        <div class="alert alert-${alert} alert-dismissible fade show" role="alert" style="margin-top: 10px;">
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
      </div>
      `
      }

    upload() {  
        // console.log(progress, progress_wrapper, progress_status, upload_btn, loading_btn, cancel_btn);

        if (! this.input.value) {
            progress_wrapper.classList.add("d-none");
            this.show_alert("No file selected", "warning")
            return;
        } 
        progress_wrapper.classList.remove("d-none");
        alert_wrapper.classList.add("d-none");
        cancel_btn.classList.remove("d-none");
        this.input.disabled = true;
        upload_btn.classList.add("d-none");
        loading_btn.classList.remove("d-none");
        
        this.initFileUpload();
        this.create_progress_bar();
    }

    initFileUpload() { 
        this.file = this.input.files[0];
        this.upload_file(0, null);
    }

    //upload file
    upload_file(start, model_id) {
        var end;
        var self = this;
        var existingPath = model_id;
        var formData = new FormData();
        var nextChunk = start + this.max_length + 1;
        var currentChunk = this.file.slice(start, nextChunk);
        var uploadedChunk = start + currentChunk.size
        if (uploadedChunk >= this.file.size) {
            end = 1;
        } else {
            end = 0;
        }

        $('.textbox').text("Uploading file : " + this.file.name);

        formData.append('file', currentChunk);
        formData.append('filename', this.file.name);
        formData.append('end', end);
        formData.append('path', existingPath);
        formData.append('nextSlice', nextChunk);
        formData.append('aborted', this.aborted);
        formData.append('id_presta', id_presta);

        $.ajaxSetup({
            headers: {
                "X-CSRFToken": document.querySelector('[name=csrfmiddlewaretoken]').value,
            }
        });
        this.xhrajax = $.ajax({
            xhr: function () {
                var xhr = new XMLHttpRequest();
                xhr.upload.addEventListener('progress', function (e) {
                    if (e.lengthComputable) {
                        if (self.file.size < self.max_length) {
                            var percent = Math.round((e.loaded / e.total) * 100);
                        } else {
                            var percent = Math.round((uploadedChunk / self.file.size) * 100);
                        }
                        $('.progress-bar').css('width', percent + '%')
                        $('.progress-bar').text(percent + '%')
                    }
                });
                
                return xhr;
            },

            url: '/upload/file',
            type: 'POST',
            dataType: 'json',
            cache: false,
            processData: false,
            contentType: false,
            data: formData,
            error: function (xhr) {
                self.reset();
                self.show_alert(xhr.statusText, "warning");
            },
            success: function (res) {
                if (nextChunk < self.file.size) {
                    // upload file in chunks
                    existingPath = res.existingPath
                    if( existingPath !='Aborted')
                        self.upload_file(nextChunk, existingPath);
                    else {
                        self.xhrajax.abort();
                        self.reset();
                        self.show_alert(`Upload Aborted`, "warning");
                    }

                } else {
                    // upload complete
                    $('.textbox').text(res.data);
                    self.reset();
                    self.show_alert(`Upload complet`, "success");
                }
            }
        });
        //if(this.aborted==2) {this.xhrajax.abort() ; }
       // if(this.aborted==1) {this.aborted=2; }
    };
}
var uploader;
(function ($) {
    $('#upload_btn').on('click', (event) => {
        event.preventDefault();
        uploader = new FileUpload(document.querySelector('#fileupload'))
        console.log(document.querySelector('#fileupload'));
        uploader.upload();
    });
})(jQuery);

(function ($) {
    $('#cancel_btn').on('click', (event) => {
        console.log("Upload canceled");
        uploader.aborted=1;
       // uploader.xhrajax.abort();
    });
})(jQuery);

/*
ondragenter = function(evt) {
    evt.preventDefault();
    evt.stopPropagation();
};

ondragover = function(evt) {
    evt.preventDefault();
    evt.stopPropagation();
};

ondragleave = function(evt) {
    evt.preventDefault();
    evt.stopPropagation();
};
  
ondrop = function(evt) {
    evt.preventDefault();
    evt.stopPropagation();
    const files = evt.originalEvent.dataTransfer;
    var uploader = new FileUpload(files);
    uploader.upload();
};

$('#dropBox')
    .on('dragover', ondragover)
    .on('dragenter', ondragenter)
    .on('dragleave', ondragleave)
    .on('drop', ondrop);
    */