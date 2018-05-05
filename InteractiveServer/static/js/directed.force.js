function removeDuplicates(myArr, prop) {
    return myArr.filter((obj, pos, arr) => {
        return arr.map(mapObj => mapObj[prop]).indexOf(obj[prop]) === pos;
    });
}

function createV4SelectableForceDirectedGraph(svgDirectedForce, graph, selectedId) {
  var width = 960,
  height = 600;

  let parentWidth = 960;
  let parentHeight = 600;

  var svgDirectedForce = d3v4.select('#svgDirectedForce')
    .attr('width', parentWidth)
    .attr('height', parentHeight)

  svgDirectedForce.selectAll("*").remove();

  // remove any previous graphs
  svgDirectedForce.selectAll('.g-main').remove();

  var gMain = svgDirectedForce.append('g')
    .classed('g-main', true);

  svgDirectedForce.append('text')
      .attr('id', 'infoPlayerName')
      .attr('x', 10)
      .attr('y', height - 80)
      .style('fill', 'orange')
      .style('font-weight', 'bold')
  svgDirectedForce.append('text')
      .attr('id', 'infoPlayerPagerank')
      .attr('x', 10)
      .attr('y', height - 60)
      .style('font-size', 8)
      .text('')
  svgDirectedForce.append('text')
      .attr('id', 'infoPlayerDegree')
      .attr('x', 10)
      .attr('y', height - 50)
      .style('font-size', 8)
      .text('')
  svgDirectedForce.append('text')
      .attr('id', 'infoPlayerCloseness')
      .attr('x', 10)
      .attr('y', height - 40)
      .style('font-size', 8)
      .text('')
  svgDirectedForce.append('text')
      .attr('id', 'infoPlayerBetweennes')
      .attr('x', 10)
      .attr('y', height - 30)
      .style('font-size', 8)
      .text('');

  var rect = gMain.append('rect')
    .attr('width', parentWidth)
    .attr('height', parentHeight)

  var gDraw = gMain.append('g');

  zoom = d3v4.zoom()
  .on('zoom', zoomed)

  gMain.call(zoom);


  function zoomed() {
    gDraw.attr('transform', d3v4.event.transform);
  }

  var color = d3v4.scaleOrdinal(d3v4.schemeCategory20);

  if (! ("links" in graph)) {
    console.log("Graph is missing links");
    return;
  }

  link = gDraw.append("g")
    .attr("class", "link")
    .selectAll("line")
    .data(graph.links)
    .enter().append("line");

  node = gDraw.append("g")
    .attr("class", "node")
    .selectAll("circle")
    .data(graph.nodes)
    .enter().append("circle")
    .attr("r", function(d) {
      var x = document.getElementById("centrality-selector").value;
      return Math.sqrt((d[x] || 0.01) * 50 );
    })
    .attr("class", function(d) {
      return d.id == selectedId ? 'ego' : '';
    })
    .on('click', function (d) {
      $("#loading-modal").modal("show");
      d3v4.json('user/' + d.id, function(error, graph) {
          $("#loading-modal").modal("hide");
          if (!error) {
              createV4SelectableForceDirectedGraph(svgDirectedForce, graph, d.id);
          } else {
              console.error(error);
          }
        });
    })
    .on("mouseover", function(d) {
      svgDirectedForce.select("#infoPlayerName").text(d.name);
      svgDirectedForce.select("#infoPlayerPagerank").text("Pagerank: " + d.pagerank);
      svgDirectedForce.select("#infoPlayerDegree").text("Degree-Centrality: " + d.degree_centrality);
      svgDirectedForce.select("#infoPlayerCloseness").text("Closeness: " + d.betweenness);
      svgDirectedForce.select("#infoPlayerBetweennes").text("Betweennes: " + d.closeness);
    })
    .call(d3v4.drag()
      .on("start", dragstarted)
      .on("drag", dragged)
      .on("end", dragended));


node.append("title")
  .text(function(d) {
    if (d.type == 'game')
      return d.name;
    else
      return d.realname;
  });

simulation = d3v4.forceSimulation()
  .force("link", d3v4.forceLink()
  .id(function(d) { return d.id; })
  .distance(function(d) {
      return 100;
      //var dist = 20 / d.value;
      //console.log('dist:', dist);

      return dist;
    })
  )
  .force("charge", d3v4.forceManyBody())
  .force("center", d3v4.forceCenter(parentWidth / 2, parentHeight / 2))
  .force("x", d3v4.forceX(parentWidth/2))
  .force("y", d3v4.forceY(parentHeight/2));

simulation
  .nodes(graph.nodes)
  .on("tick", ticked);

simulation.force("link")
.links(graph.links);

  function ticked() {
    // update node and line positions at every step of
    // the force simulation
    link.attr("x1", function(d) { return d.source.x; })
    .attr("y1", function(d) { return d.source.y; })
    .attr("x2", function(d) { return d.target.x; })
    .attr("y2", function(d) { return d.target.y; });

    node.attr("cx", function(d) { return d.x; })
    .attr("cy", function(d) { return d.y; });
  }

  function dragstarted(d) {
    if (!d3v4.event.active) simulation.alphaTarget(0.9).restart();

    if (!d.selected) {
      node.classed("selected", function(p) { return p.selected =  p.previouslySelected = false; });
    }

    d3v4.select(this).classed("selected", function(p) { d.previouslySelected = d.selected; return d.selected = true; });

    node.filter(function(d) { return d.selected; })
    .each(function(d) { //d.fixed |= 2;
      d.fx = d.x;
      d.fy = d.y;
    })

  }

  function dragged(d) {
    node.filter(function(d) { return d.selected; })
    .each(function(d) {
      d.fx += d3v4.event.dx;
      d.fy += d3v4.event.dy;
    })
  }

  function dragended(d) {
    if (!d3v4.event.active) simulation.alphaTarget(0);
    d.fx = null;
    d.fy = null;
    node.filter(function(d) { return d.selected; })
    .each(function(d) { //d.fixed &= ~6;
      d.fx = null;
      d.fy = null;
    })
  }

  return graph;
};
