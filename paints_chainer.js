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

  $('#wPaint').wPaint({
    path: '/wPaint/',
    menuOffsetLeft: -35,
    menuOffsetTop: -50
  });

  $('#painting_label').hide();
  $('#submit').prop('disabled', true);
  $('#submit').click(function () {
    if (!$('#background').attr('src')) {
      alert('select a file');
    } else {
      colorize();
    }
  });
  $('#img_pane').hide();

  $('#load_line_file').on('change', function (e) {
    var file = e.target.files[0];

    if (file.type.indexOf('image') < 0) {
      return false;
    }

    set_file(file);
  });

  $('#output').bind('load', function () {
    $('#output')
      .height($('#background').height())
      .width($('#background').width());
    $('#img_pane')
      .width($('#output').width() * 2.3 + 24)
      .height($('#output').height() + 20);
  });

  $('#background').load(function () {
    $('#wPaint')
      .width($('#background').width())
      .height($('#background').height());

    $('#wPaint').wPaint('resize');
    $('#submit').prop('disabled', true);

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
    $.ajax({
      type: 'POST',
      url: '/post',
      data: data,
      cache: false,
      contentType: false,
      processData: false,
      dataType: 'text', // server response is broken
      beforeSend: function () {
        $('#painting_label').show();
        $('#submit').prop('disabled', true);
        console.log('coloring start');
      },
      success: function () {
        console.log('uploaded');
        var now = new Date().getTime();
        $('#output').attr('src', '/images/out/' + image_id + '_0.jpg?' + now);
        $('#output_min').attr('src', '/images/out_min/' + image_id + '_0.png?' + now);
      },
      complete: function () {
        $('#painting_label').hide();
        $('#submit').prop('disabled', false);
        console.log('coloring finish');
      }
    });
  }

  function toBlob(img, fn) {
    var canvas = document.createElement('canvas');
    canvas.width = img.naturalWidth || img.width;
    canvas.height = img.naturalHeight || img.height;
    canvas.getContext('2d').drawImage(img, 0, 0, canvas.width, canvas.height);
    canvas.toBlob(fn);
  }

  function colorize(new_image_id) {
    toBlob($('#background')[0], function (line_blob) {
      var ajaxData = new FormData();
      if (new_image_id) {
        ajaxData.append('line', line_blob);
        image_id = new_image_id;
      }
      $('#wPaint').wPaint('imageCanvas').toBlob(function (ref_blob) {
        if (ref_blob.size > 30000) {
          alert('file size over');
          return;
        }
        ajaxData.append('ref', ref_blob);
        ajaxData.append('blur', $('#blur_k').val());
        ajaxData.append('id', image_id);
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
