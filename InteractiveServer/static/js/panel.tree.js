(function(){

  var margin = {top: 50, right: 0, bottom: 0, left: 0},
      width = 900,
      height = 600 - margin.top - margin.bottom,
      formatNumber = d3.format(",d"),
      transitioning;

  var x = d3.scale.linear()
      .domain([0, width])
      .range([0, width]);

  var y = d3.scale.linear()
      .domain([0, height])
      .range([0, height]);

  var treemap = d3.layout.treemap()
      .children(function(d, depth) { return depth ? null : d._children; })
      .sort(function(a, b) { return a.value - b.value; })
      .ratio(height / width * 0.5 * (1 + Math.sqrt(5)))
      .round(false);

  var svg = d3.select("#chart").append("svg")
      .attr("width", width + margin.left + margin.right)
      .attr("height", height + margin.bottom + margin.top)
      .style("margin-left", -margin.left + "px")
      .style("margin.right", -margin.right + "px")
    .append("g")
      .attr("transform", "translate(" + margin.left + "," + margin.top + ")")
      .style("shape-rendering", "crispEdges");

  var grandparent = svg.append("g")
      .attr("class", "grandparent");

  grandparent.append("rect")
      .attr("y", -margin.top)
      .attr("width", width)
      .attr("height", margin.top);

  grandparent.append("text")
      .attr("x", 6)
      .attr("y", 6 - margin.top)
      .attr("width", width)
      .attr("dy", "0.75em");

  d3.json("/genres", function(root) {
    initialize(root);
    accumulate(root);
    layout(root);
    display(root);

    function initialize(root) {
      root.x = root.y = 0;
      root.dx = width;
      root.dy = height;
      root.depth = 0;
    }

    function accumulate(d) {
      return (d._children = d.children)
          ? d.value = d.children.reduce(function(p, v) { return p + accumulate(v); }, 0)
          : d.value;
    }

    function layout(d) {
      if (d._children) {
        treemap.nodes({_children: d._children});
        d._children.forEach(function(c) {
          c.x = d.x + c.x * d.dx;
          c.y = d.y + c.y * d.dy;
          c.dx *= d.dx;
          c.dy *= d.dy;
          c.parent = d;
          layout(c);
        });
      }
    }

    function display(d) {
      grandparent
          .datum(d.parent)
          .on("click", transition)
        .select("text")
          .text(name(d));

      var g1 = svg.insert("g", ".grandparent")
          .datum(d)
          .attr("class", "depth");

      var g = g1.selectAll("g")
          .data(d._children)
        .enter().append("g");

      g.filter(function(d) { return d._children; })
          .classed("children", true)
          .on("click", transition);

      var pattern_def = svg.append("defs");  //append defs in svg

      g.selectAll(".child")
          .data(function(d) { return d._children || [d]; })
        .enter().append("rect")
          .attr("class", "child")
          .each(function(d,i) {
              if ('logo' in d) {
                if (document.getElementById("node-img" + d.steamid) == undefined) {
                  pattern_def.append("pattern")
                    .attr("id", "node-img" + d.steamid)
                    .attr("patternUnits", "objectBoundingBox")
                    .attr({
                        "width": "100%",
                        "height": "100%"
                    })
                    .attr({
                        "viewBox": "0 0 1 1"
                    })
                    .append("image")
                    .attr("xlink:href", d.logo)
                    .attr({
                        "x": 0,
                        "y": 0,
                        "width": "1",
                        "height": "1",
                        "preserveAspectRatio": "none"
                    })
                  }
                  d3.select(this).attr("fill", "url(#node-img" + d.steamid + ")")
              }
          })
          .call(rect);

      g.append("rect")
          .attr("class", "parent")
          .each(function(d,i) {
              if ('logo' in d) {
                d3.select(this).attr("fill", "url(#node-img" + d.steamid + ")")
              }
          })
          .on('click', function(d, i) {
            d3.json('/games/' + d.steamid, function(error, json) {
              var template = $("#info-game-template").html();
              $("#info-game-modal .modal-dialog").html(Mustache.render(template, json.data));
              $("#info-game-modal").modal("show");
            })
          })
          .call(rect)
        .append("title")
          .text(function(d) { return formatNumber(d.value); });

      g.filter(function(d) {return (!d.logo)})
        .append("text")
        .attr("dy", ".75em")
        .text(function(d) {return d.name; })
        .call(text);

      g.filter(function(d) {return (!d.logo)}).insert("rect", "text")
        .attr("class", "label")
        .attr("x", function(d){return d.bbox.x - 4})
        .attr("y", function(d){return d.bbox.y - 4})
        .attr("width", function(d){return d.bbox.width + 8 })
        .attr("height", function(d){return d.bbox.height + 8 })
        .style("fill", "#59616d");

      function text(text) {
        text.attr("x", function(d) { return x(d.x) + 6; })
            .attr("y", function(d) { return y(d.y) + 6; });
        text.each(function(d) { d.bbox = this.getBBox(); })
      }

      function rect(rect) {
        rect.attr("x", function(d) { return x(d.x); })
            .attr("y", function(d) { return y(d.y); })
            .attr("width", function(d) { return x(d.x + d.dx) - x(d.x); })
            .attr("height", function(d) { return y(d.y + d.dy) - y(d.y); })
      }

      function rectLabel(rect) {
        rect.attr("x", function(d) { return x(d.x); })
            .attr("y", function(d) { return y(d.y); });
      }

      function name(d) {
        return d.name;
      }

      function transition(d) {
        if (transitioning || !d) return;
        transitioning = true;

        var g2 = display(d),
            t1 = g1.transition().duration(750),
            t2 = g2.transition().duration(750);

        // Update the domain only after entering new elements.
        x.domain([d.x, d.x + d.dx]);
        y.domain([d.y, d.y + d.dy]);

        // Enable anti-aliasing during the transition.
        svg.style("shape-rendering", null);

        // Draw child nodes on top of parent nodes.
        svg.selectAll(".depth").sort(function(a, b) { return a.depth - b.depth; });

        // Fade-in entering text.
        g2.selectAll("text").style("fill-opacity", 0);

        // Transition to the new view.
        t1.selectAll("text").call(text).style("fill-opacity", 0);
        t2.selectAll("text").call(text).style("fill-opacity", 1);
        t1.selectAll(".label").call(rectLabel).style("fill-opacity", 0);
        t2.selectAll(".label").call(rectLabel).style("fill-opacity", 1);
        t1.selectAll("rect:not(.label)").call(rect);
        t2.selectAll("rect:not(.label)").call(rect);

        // Remove the old node when the transition is finished.
        t1.remove().each("end", function() {
          svg.style("shape-rendering", "crispEdges");
          transitioning = false;
        });
      }

      return g;
    }
  });
})()
