(function ($) {
  var img = 'plugins/shapes/img/icons-menu-main-shapes.png';

  // extend menu
  $.extend(true, $.fn.wPaint.menus.main.items, {
    rectangle: {
      group: 'shapes'
    },
    roundedRect: {
      icon: 'activate',
      group: 'shapes',
      title: 'Rounded Rectangle',
      img: img,
      index: 0,
      callback: function () { this.setMode('roundedRect'); }
    },
    square: {
      icon: 'activate',
      group: 'shapes',
      title: 'Square',
      img: img,
      index: 1,
      callback: function () { this.setMode('square'); }
    },
    roundedSquare: {
      icon: 'activate',
      group: 'shapes',
      title: 'Rounded Square',
      img: img,
      index: 2,
      callback: function () { this.setMode('roundedSquare'); }
    },
    diamond: {
      icon: 'activate',
      group: 'shapes',
      title: 'Diamond',
      img: img,
      index: 4,
      callback: function () { this.setMode('diamond'); }
    },

    ellipse: {
      group: 'shapes2'
    },
    circle: {
      icon: 'activate',
      group: 'shapes2',
      title: 'Circle',
      img: img,
      index: 3,
      callback: function () { this.setMode('circle'); }
    },
    pentagon: {
      icon: 'activate',
      group: 'shapes2',
      title: 'Pentagon',
      img: img,
      index: 5,
      callback: function () { this.setMode('pentagon'); }
    },
    hexagon: {
      icon: 'activate',
      group: 'shapes2',
      title: 'Hexagon',
      img: img,
      index: 6,
      callback: function () { this.setMode('hexagon'); }
    }
  });

  // extend functions
  $.fn.wPaint.extend({
    /****************************************
     * roundedRect
     ****************************************/
    _drawRoundedRectDown: function (e) { this._drawShapeDown(e); },

    _drawRoundedRectMove: function (e) {
      this._drawShapeMove(e);

      var radius = e.w > e.h ? e.h / e.w : e.w / e.h;

      this.ctxTemp.roundedRect(e.x, e.y, e.w, e.h, Math.ceil(radius * (e.w * e.h * 0.001)));
      this.ctxTemp.stroke();
      this.ctxTemp.fill();
    },

    _drawRoundedRectUp: function (e) {
      this._drawShapeUp(e);
      this._addUndo();
    },

    /****************************************
     * square
     ****************************************/
    _drawSquareDown: function (e) { this._drawShapeDown(e); },

    _drawSquareMove: function (e) {
      this._drawShapeMove(e);

      var l = e.w > e.h ? e.h : e.w;

      this.ctxTemp.rect(e.x, e.y, l, l);
      this.ctxTemp.stroke();
      this.ctxTemp.fill();
    },

    _drawSquareUp: function (e) {
      this._drawShapeUp(e);
      this._addUndo();
    },

    /****************************************
     * roundedSquare
     ****************************************/
    _drawRoundedSquareDown: function (e) { this._drawShapeDown(e); },

    _drawRoundedSquareMove: function (e) {
      this._drawShapeMove(e);

      var l = e.w > e.h ? e.h : e.w;

      this.ctxTemp.roundedRect(e.x, e.y, l, l, Math.ceil(l * l * 0.001));
      this.ctxTemp.stroke();
      this.ctxTemp.fill();
    },

    _drawRoundedSquareUp: function (e) {
      this._drawShapeUp(e);
      this._addUndo();
    },

    /****************************************
     * diamond
     ****************************************/
    _drawDiamondDown: function (e) { this._drawShapeDown(e); },

    _drawDiamondMove: function (e) {
      this._drawShapeMove(e);

      this.ctxTemp.diamond(e.x, e.y, e.w, e.h);
      this.ctxTemp.stroke();
      this.ctxTemp.fill();
    },

    _drawDiamondUp: function (e) {
      this._drawShapeUp(e);
      this._addUndo();
    },

    /****************************************
     * circle
     ****************************************/
    _drawCircleDown: function (e) { this._drawShapeDown(e); },

    _drawCircleMove: function (e) {
      this._drawShapeMove(e);

      var l = e.w > e.h ? e.h : e.w;

      this.ctxTemp.ellipse(e.x, e.y, l, l);
      this.ctxTemp.stroke();
      this.ctxTemp.fill();
    },

    _drawCircleUp: function (e) {
      this._drawShapeUp(e);
      this._addUndo();
    },

    /****************************************
     * pentagon
     ****************************************/
    _drawPentagonDown: function (e) { this._drawShapeDown(e); },

    _drawPentagonMove: function (e) {
      this._drawShapeMove(e);

      this.ctxTemp.pentagon(e.x, e.y, e.w, e.h);
      this.ctxTemp.stroke();
      this.ctxTemp.fill();
    },

    _drawPentagonUp: function (e) {
      this._drawShapeUp(e);
      this._addUndo();
    },

    /****************************************
     * hexagon
     ****************************************/
    _drawHexagonDown: function (e) { this._drawShapeDown(e); },

    _drawHexagonMove: function (e) {
      this._drawShapeMove(e);

      this.ctxTemp.hexagon(e.x, e.y, e.w, e.h);
      this.ctxTemp.stroke();
      this.ctxTemp.fill();
    },

    _drawHexagonUp: function (e) {
      this._drawShapeUp(e);
      this._addUndo();
    }
  });
})(jQuery);
