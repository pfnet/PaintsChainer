var image_id;

// cf. https://github.com/websanova/wPaint/blob/master/src/wPaint.js#L243
$.fn.wPaint.extend({
  getImageCanvas: function (withBg) { // getCanvas is bad name (conflict).
    var canvasSave = document.createElement('canvas'),
        ctxSave = canvasSave.getContext('2d');

    withBg = withBg === false ? false : true;

    $(canvasSave)
      .css({display: 'none', position: 'absolute', left: 0, top: 0})
      .attr('width', this.width)
      .attr('height', this.height);

    if (withBg) { ctxSave.drawImage(this.canvasBg, 0, 0); }
    ctxSave.drawImage(this.canvas, 0, 0);

    return canvasSave;
  }
});

$(function () {
  image_id = 'test_id';

  $('#img_pane').show(); // for $.fn.wPaint
  $('#wPaint').wPaint({
    path: '/wPaint/',
    menuOffsetLeft: -35,
    menuOffsetTop: -50
  });
  $('#img_pane').hide();

  $('#submit').click(function () {
    if (!$('#background').attr('src')) {
      alert('select a file');
    } else {
      colorize();
    }
  });

  $('#load_line_file').on('change', function (e) {
    var file = e.target.files[0];

    if (file.type.indexOf('image') < 0) {
      return false;
    }

    set_file(file);
  });

  $('#background').load(function () {
    $('#wPaint')
      .width($('#background').width())
      .height($('#background').height())
      .wPaint('resize');
    var wPaintOuterWidth = $('#wPaint').outerWidth(true);
    $('#img_pane .span6').width(wPaintOuterWidth);
    $('#img_pane').width(wPaintOuterWidth * 2 + 30);
    colorize(uniqueid()); // update image_id
  });

  //--- functions

  function uniqueid() {
    var idstr = String.fromCharCode(Math.floor((Math.random() * 25) + 65));
    do {
      var ascicode = Math.floor((Math.random() * 42) + 48);
      if (ascicode < 58 || ascicode > 64) {
        idstr += String.fromCharCode(ascicode);
      }
    } while (idstr.length < 32);
    return idstr;
  }

  function paint(data) {
    var origin = '';
    if (location.hostname === 'paintschainer.preferred.tech') {
      origin = 'http://paintschainer' + (Math.floor(Math.random() * 5) + 1) + '.preferred.tech'; // 1 ~ 5
    }
    $.ajax({
      type: 'POST',
      url: origin + '/post',
      data: data,
      cache: false,
      contentType: false,
      processData: false,
      dataType: 'text', // server response is broken
      beforeSend: function () {
        $('#painting_status').attr('class', '').text('NOW COLORING ...').show();
        $('#submit').prop('disabled', true);
        console.log('coloring start');
      },
      success: function () {
        console.log('uploaded');
        $('#painting_status').hide();
        var now = new Date().getTime();
        $('#output').attr('src', origin + '/images/out/' + image_id + '_0.jpg?' + now).show();
        $('#output_min').attr('src', origin + '/images/out_min/' + image_id + '_0.png?' + now).show();
      },
      error: function () {
        $('#painting_status').attr('class', 'text-error').text('SERVER ERROR').show();
      },
      complete: function () {
        $('#submit').prop('disabled', false);
        console.log('coloring finish');
      }
    });
  }

  function blobUrlToBlob(url, fn) {
    var xhr = new XMLHttpRequest();
    xhr.onload = function () {
      fn(xhr.response);
    };
    xhr.responseType = 'blob';
    xhr.open('GET', url);
    xhr.send();
  }

  function colorize(new_image_id) {
    $('#wPaint').wPaint('imageCanvas').toBlob(function (ref_blob) {
      if (ref_blob.size > 30000) {
        alert('file size over');
        return;
      }
      var ajaxData = new FormData();
      ajaxData.append('id', new_image_id || image_id);
      ajaxData.append('blur', $('#blur_k').val());
      ajaxData.append('ref', ref_blob);
      if ( new_image_id ) {
        image_id = new_image_id;
      }
      blobUrlToBlob($('#background').attr('src'), function (line_blob) {
        ajaxData.append('line', line_blob);
        paint(ajaxData);
      });
    });
  };

  function set_file(file) {
    console.log('set file');
    $('#img_pane').show('fast', function () {
      $('#background').attr('src', window.URL.createObjectURL(file));
    });
  };
});
