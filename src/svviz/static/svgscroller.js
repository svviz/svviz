(function () {
'use strict';

var $ = jQuery;

var name = 'SVGScroller';


function Scrollbar(scrollpanel, $host, options) {
    var self = this;

    self.settings = $.extend({}, {"vertical": true, "endSpace":10}, options || {});    
    self.orientation = self.settings.vertical ? "vert" : "horiz";
    self.$host = $host;

    self.$scrollbar = $('<div class="scrollbar ' + self.orientation + '"/>');
    self.$thumb = $('<div class="thumb '  + self.orientation + '"/>').appendTo(self.$scrollbar);

    self.$host.append(self.$scrollbar);
    self.mouseOffset = 0;
    self.scrollval = 0;

    self.active = true;

    self.resize = function(size, viewable, viewsize) {
        if (self.settings.vertical) {
            self.scrollbarSize = size - self.settings.endSpace;
            self.$scrollbar.height(self.scrollbarSize);
            self.thumbsize = (viewable / viewsize) * self.scrollbarSize;
            self.thumbsize = Math.max(self.thumbsize, 10);
            self.$thumb.height(Math.min(self.scrollbarSize, self.thumbsize));
        } else {
            self.scrollbarSize = size - self.settings.endSpace;
            self.$scrollbar.width(self.scrollbarSize);
            self.thumbsize = (viewable / viewsize) * self.scrollbarSize;
            self.thumbsize = Math.max(self.thumbsize, 10);
            self.$thumb.width(Math.min(self.scrollbarSize, self.thumbsize));
        }

        if (self.thumbsize >= self.scrollbarSize) {
            self.$scrollbar.fadeTo(50, 0.8);
            self.$thumb.fadeTo(50, 0.0);
            self.active = false;
        } else {
            self.active = true;
            self.$scrollbar.fadeTo(50, 1);
            self.$thumb.fadeTo(50, 1);
        }
    }

    self.scrollTo = function(newposition) {
        if (!self.active){
            return;
        }

        if (newposition < 0) {
            newposition = 0;
        } else if (newposition > self.scrollbarSize-self.thumbsize) {
            newposition = self.scrollbarSize-self.thumbsize;
        }


        if (self.settings.vertical) {
            self.$thumb.css({"top": newposition});
        } else {
            self.$thumb.css({"left": newposition});
        }
        console.log("HERE:" + self.thumbsize);

        self.scrollval = newposition / (self.scrollbarSize-self.thumbsize);
        scrollpanel.scroll();
    }

    self.onMouseDrag = function(event) {
        if (!self.active){
            return;
        }

        var clickFrac;
        if (self.settings.vertical) {
            clickFrac = (event.pageY - self.$scrollbar.offset().top - self.mouseOffset) / self.scrollbarSize;
        } else {
            clickFrac = (event.pageX - self.$scrollbar.offset().left - self.mouseOffset) / self.scrollbarSize;
        }

        self.scrollTo(clickFrac * self.scrollbarSize);

        event.preventDefault();
        event.stopPropagation();
    }

    self.page = function(distance) {
        var newscroll;

        if (!self.active){
            return;
        }

        if (self.settings.vertical) {
            newscroll = self.$thumb.position().top + (self.thumbsize*distance);
        } else {
            newscroll = self.$thumb.position().left + (self.thumbsize*distance);
        }

        // console.log(newscroll);
        self.scrollTo(newscroll);
    }

    self.curscroll = function() {
        if (self.settings.vertical) {
            return self.$thumb.position().top;
        } else {
            return self.$thumb.position().left;
        }
    }

    self.$thumb.on("mousedown", function(event) {
        if (!self.active){
            return;
        }

        if (self.settings.vertical) {
            self.mouseOffset = event.pageY - self.$thumb.offset().top;
        } else {
            self.mouseOffset = event.pageX - self.$thumb.offset().left;
        }

        self.$thumb.addClass('active');

        $(window)
            .on('mousemove', self.onMouseDrag)
            .one('mouseup', function (event) {
                self.$thumb.removeClass('active');
                $(window).off('mousemove', self.onMouseDrag);
            });

        event.preventDefault();
        event.stopPropagation();
    })

    self.$scrollbar.on("mousedown", function(event) {
        if (!self.active){
            return;
        }

        if (event.altKey){
            // jump to clicked position
            var clickFrac;
            if (self.settings.vertical) {
                clickFrac = (event.pageY - self.$scrollbar.offset().top - self.thumbsize/2.0) / self.scrollbarSize;
            } else {
                clickFrac = (event.pageX - self.$scrollbar.offset().left - self.thumbsize/2.0) / self.scrollbarSize;
            }
            self.scrollTo(clickFrac * self.scrollbarSize);
        } else {
            // scroll a page in the direction of the click
            var direction = 1;
            if (self.settings.vertical) {
                if (event.pageY < self.$thumb.offset().top){
                    direction = -1;
                }
            } else {
                if (event.pageX < self.$thumb.offset().left){
                    direction = -1;
                }
            }
            self.page(direction);
        }
    })

    self.resize();
}

function ScrollPanel(element, options, svg_tags) {
    var self = this;

    svg_tags = typeof svg_tags !== 'undefined' ? svg_tags : "";
    self.$element = $(element);
    self.$views = self.$element.find(svg_tags+" .one_svg")
    self.nviews = self.$views.length;

    self.xmin = 1e100;
    self.xmax = 0;
    self.yviewsizes = [];

    self.containerwidth = self.$element.width();
    self.containerheight = self.$element.height();

    self.xscrollbar = new Scrollbar(self, self.$element, {"vertical":false});
    self.yscrollbars = [];

    self.yviewables = [];

    self.$views.each(function(i){
        var newyscrollbar = new Scrollbar(self, $(this), {"vertical":true, "endSpace":0});
        self.yscrollbars.push(newyscrollbar);

        var bbox = $(this).find(".svg_viewport")[0].getBBox();

        self.xmin = Math.min(self.xmin, bbox.x);
        self.xmax = Math.max(self.xmax, bbox.x+bbox.width);

        self.yviewsizes.push(bbox.height + 550);

        // $(this).width(self.$element.width());
        // $(this).height((self.$element.height()-12)/self.nviews);

        $(this).width("100%");
        $(this).height("calc("+100.0/self.nviews+"% - 12px)");


        self.yviewables.push(0);
    })

    self.xzoom = self.containerwidth / (self.xmax-self.xmin);
    self.yzooms = self.$views.map(function(){return self.xzoom;});


    self.zoom = function() {
        self.xviewable = self.containerwidth / self.xzoom;
        for (var i=0; i < self.yviewables.length; i++) {
            self.yviewables[i] = self.containerheight / self.yzooms[i] / self.nviews;
        }
        // console.log(":::>");
        // console.log(self.yzooms);
        // console.log(":::<");
    }

    self.scroll = function() {
        self.$views.each(function(i, j){
            var xscroll = ((self.xmax-self.xmin) - self.xviewable) * (self.xscrollbar.scrollval) + self.xmin;
            var yscroll = (self.yviewsizes[i] - self.yviewables[i]) * (self.yscrollbars[i].scrollval);
            var viewBox = [xscroll, yscroll, self.xviewable, self.yviewables[i]];

            $(this).find("svg")[0].setAttribute("viewBox", viewBox.join(" "));
        })
    }

    self.scrollToBottom = function() {
        self.yscrollbars.forEach(function(scrollbar){
            scrollbar.scrollTo(1e100);
        });
    }

    self.moveView = function(deltax, deltay){
        self.xscrollbar.scrollTo(self.xscrollbar.curscroll()+deltax);
        self.yscrollbars.forEach(function(scrollbar, i){
            scrollbar.scrollTo(scrollbar.curscroll()+deltay);
        });
        self.update();
    }

    self.update = function() {
        self.xscrollbar.resize($(self.$views[0]).width(), self.xviewable, self.xmax-self.xmin);

        self.yscrollbars.forEach(function(scrollbar, i){
            scrollbar.resize($(self.$views[i]).height(), self.yviewables[i], self.yviewsizes[i]);
        });
        self.zoom();
        self.scroll();
    }


    self.$element.on("mousedown", function(mouseDownEvent){
        var scrollStartX = mouseDownEvent.pageX;
        var scrollStartY = mouseDownEvent.pageY;

        var onMouseDrag = function(dragevent) {
            console.log("::" + dragevent.pageX + " * " + scrollStartX + ":" + (dragevent.pageX - scrollStartX) + "::" + dragevent.pageY + " * " + scrollStartY + ":" + (dragevent.pageY - scrollStartY));
            self.moveView(scrollStartX - dragevent.pageX, scrollStartY - dragevent.pageY);

            scrollStartX = dragevent.pageX;
            scrollStartY = dragevent.pageY;

            dragevent.preventDefault();
            dragevent.stopPropagation();
        }

        $(window)
            .on('mousemove', onMouseDrag)
            .one('mouseup', function (event) {
                $(window).off('mousemove', onMouseDrag);
            });

        mouseDownEvent.preventDefault();
        mouseDownEvent.stopPropagation();
    });

    self.$element.on("mousewheel", function(event){
        // console.log(event.deltaX, event.deltaY, event.deltaFactor, event.altKey);

        if (event.altKey){
            var zoomFactor;
            zoomFactor = event.deltaY > 0 ? Math.pow(1.25, Math.min(3,event.deltaY)) : Math.pow(0.8, -(Math.max(-3, event.deltaY)));
            self.xzoom *= zoomFactor;
            for (var i=0; i < self.yzooms.length; i++){
                self.yzooms[i] *= zoomFactor;
            }

            self.update();
        } else {
            if (event.deltaX != 0) {
                self.xscrollbar.page(event.deltaX*0.05);
            }
            if (event.deltaY != 0) {
                for (var i=0; i < self.yscrollbars.length; i++) {
                    self.yscrollbars[i].page(-event.deltaY*0.05);
                }
            }
        }

        event.preventDefault();
        event.stopPropagation();
    });
    // Initial update.
    self.update();
}

// Register the plug in
// --------------------
$.fn[name] = function (options, options2) {
    return this.each(function () {
        var $this = $(this);
        var scrollpanel = $this.data(name);

        if (!scrollpanel) {
            scrollpanel = new ScrollPanel(this, options);
            scrollpanel.update();
            scrollpanel.scrollToBottom();
            $this.data(name, scrollpanel);
        }

        if (options === 'update') {
            scrollpanel.update(options2);
        }
    });
};

}());