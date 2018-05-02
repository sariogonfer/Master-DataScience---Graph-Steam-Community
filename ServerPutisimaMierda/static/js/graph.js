function removeDuplicates(myArr, prop) {
    return myArr.filter((obj, pos, arr) => {
        return arr.map(mapObj => mapObj[prop]).indexOf(obj[prop]) === pos;
    });
}

function createV4SelectableForceDirectedGraph(svg, graph) {
  var width = +svg.attr("width"),
  height = +svg.attr("height");

  let parentWidth = d3.select('svg').node().parentNode.clientWidth;
  let parentHeight = d3.select('svg').node().parentNode.clientHeight;

  var svg = d3.select('svg')
    .attr('width', parentWidth)
    .attr('height', parentHeight)

  // remove any previous graphs
  svg.selectAll('.g-main').remove();

  var gMain = svg.append('g')
    .classed('g-main', true);

  var rect = gMain.append('rect')
    .attr('width', parentWidth)
    .attr('height', parentHeight)
    .style('fill', 'white')

  var gDraw = gMain.append('g');

  zoom = d3.zoom()
  .on('zoom', zoomed)

  gMain.call(zoom);


  function zoomed() {
    gDraw.attr('transform', d3.event.transform);
  }

  var color = d3.scaleOrdinal(d3.schemeCategory20);

  if (! ("links" in graph)) {
    console.log("Graph is missing links");
    return;
  }

  link = gDraw.append("g")
    .attr("class", "link")
    .selectAll("line")
    .data(graph.links)
    .enter().append("line")
    .attr("stroke-width", function(d) { return Math.log(d.played_mins / 60); });

  node = gDraw.append("g")
    .attr("class", "node")
    .selectAll("circle")
    .data(graph.nodes)
    .enter().append("circle")
    .attr("r", 5)
    .attr("fill", function(d) {
      if (d.type == 'game')
        return 'red';
      else
        return 'blue';
    })
    .on('click', function (d) {
      d3.json('node/' + d.id, function(error, graph) {
          if (!error) {
            aux = Object;
            aux.nodes = graph.nodes.concat(node.data());
            aux.links = graph.links.concat(link.data());
            aux.nodes = removeDuplicates(aux.nodes, 'id')
            createV4SelectableForceDirectedGraph(svg, aux);
          } else {
            console.error(error);
          }
      });
    })
    .call(d3.drag()
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

simulation = d3.forceSimulation()
  .force("link", d3.forceLink()
  .id(function(d) { return d.id; })
  .distance(function(d) {
      return 30;
      //var dist = 20 / d.value;
      //console.log('dist:', dist);

      return dist;
    })
  )
  .force("charge", d3.forceManyBody())
  .force("center", d3.forceCenter(parentWidth / 2, parentHeight / 2))
  .force("x", d3.forceX(parentWidth/2))
  .force("y", d3.forceY(parentHeight/2));

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
    if (!d3.event.active) simulation.alphaTarget(0.9).restart();

    if (!d.selected) {
      node.classed("selected", function(p) { return p.selected =  p.previouslySelected = false; });
    }

    d3.select(this).classed("selected", function(p) { d.previouslySelected = d.selected; return d.selected = true; });

    node.filter(function(d) { return d.selected; })
    .each(function(d) { //d.fixed |= 2;
      d.fx = d.x;
      d.fy = d.y;
    })

  }

  function dragged(d) {
    node.filter(function(d) { return d.selected; })
    .each(function(d) {
      d.fx += d3.event.dx;
      d.fy += d3.event.dy;
    })
  }

  function dragended(d) {
    if (!d3.event.active) simulation.alphaTarget(0);
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
