var image_id, prev_image_id, startPaint, endPaint, colorize, enable_interactive, select_src;

$(function () {
  image_id = 'test_id';
  prev_image_id = 'none';

  $('#wPaint').wPaint({
    path: '/static/wPaint/',
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

    var reader = new FileReader();
    reader.onload = function (e) {
      select_src(e.target.result);
    };
    reader.readAsDataURL(file);
  });


  $('#set_line_url').click(function () {
    // currently not work
    select_src($('#load_line_url').val());
  });


  $('#output').bind('load', function () {
    $('#output')
      .height($('#background').height())
      .width($('#background').width());
    $('#img_pane')
      .width($('#output').width() * 2.3 + 24)
      .height($('#output').height() + 20);
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

  startPaint = function () {
    $('#painting_label').show();
    $('#submit').prop('disabled', true);
    console.log('coloring start');
  };

  endPaint = function () {
    $('#painting_label').hide();
    $('#submit').prop('disabled', false);
    console.log('coloring finish');
  };

  function toBlob(img, fn) {
    var canvas = document.createElement('canvas');
    canvas.width = img.naturalWidth || img.width;
    canvas.height = img.naturalHeight || img.height;
    canvas.getContext('2d').drawImage(img, 0, 0, canvas.width, canvas.height);
    canvas.toBlob(fn);
  }

  colorize = function () {
    startPaint();
    toBlob($('#background')[0], function (line_blob) {
      var ajaxData = new FormData();
      if (prev_image_id != image_id) {
        ajaxData.append('line', line_blob);
        prev_image_id = image_id;
      }
      // cf. https://github.com/websanova/wPaint/blob/master/src/wPaint.js#L243
      var wPaint = $('#wPaint').data('wPaint');
      var canvasSave = document.createElement('canvas'),
          ctxSave = canvasSave.getContext('2d');
      $(canvasSave)
        .css({display: 'none', position: 'absolute', left: 0, top: 0})
        .attr('width', wPaint.width)
        .attr('height', wPaint.height);

      ctxSave.drawImage(wPaint.canvasBg, 0, 0);
      ctxSave.drawImage(wPaint.canvas, 0, 0);
      canvasSave.toBlob(function (ref_blob) {
        ajaxData.append('ref', ref_blob);
        ajaxData.append('blur', $('#blur_k').val());
        ajaxData.append('id', image_id);
        $.ajax({
          url: '/post',
          data: ajaxData,
          cache: false,
          contentType: false,
          processData: false,
          type: 'POST',
          dataType: 'json',
          complete: function (data) {
            // location.reload();
            console.log('uploaded');
            var now = new Date().getTime();
            $('#output').attr('src', '/static/images/out/' + image_id + '_0.jpg?' + now);
            $('#output_min').attr('src', '/static/images/out_min/' + image_id + '_0.png?' + now);
            endPaint();
          }
        });
      });
    });
  };

  enable_interactive = function () {
    $('.wPaint-canvas').mouseup(colorize);
  };

  select_src = function (src) {
    $('#img_pane').show('fast', function () {
      image_id = uniqueid();

      $('#background').attr('src', src).load(function () {
        $('#wPaint')
          .width($('#background').width())
          .height($('#background').height());

        $('#wPaint').wPaint('resize');
        $('#submit').prop('disabled', true);
        colorize();
      });
    });
  };
});
