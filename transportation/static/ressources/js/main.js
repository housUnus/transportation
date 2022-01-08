var x = 3
	var y = 3
	var data = []
	window.onload = function () {
		$('#results').hide()
		$('#btn').click(function () {
			var data = [];
			$('#table tr.rowx').each(function () {
				var row = [];
				$(this).find('.coly > input').each(function () {
					row.push($(this).val());
				})
				data.push(row);
			})
			method = $('#methods').val()
			senddata(data, method)
		})

		function senddata(data, method) {
			$.ajax({
				type: 'POST',
				url: $("#btn").attr("data-url"),
				data: JSON.stringify({
					data: data,
					method: method
				}),
				// data:JSON.stringify({data:data}),
				success: function (data) {

					$("#results .paths").remove()
					$('#results').show()
					try {
						data = JSON.parse(data)
						data = json2array(data)
						total = 0
						if (data.length > 0) {
							data.forEach(function (path) {
								total += path[2] * path[3]
								if(path[4] == 0 && path[3] !=0){
									$("#results tbody").append(`<tr class="paths">
								<td>S${path[0]+1}</td>
								<td>D${path[1]+1}</td>
								<td>${path[2]}</td>
								<td>${path[3]}</td>
								</tr>`)
								}
							})
							$("#results tbody").append(`<tr class="paths text-center text-success font-weight-bold">
								<td colspan ="4">TOTAL COST = ${total}</td>
								</tr>`)
						}
					} catch (e) {
						$("#results tbody").append(`<tr class="paths text-center text-danger font-weight-bold text-responsive">
								<td colspan ="4">Error happend, Please check that Demande = Offer</td>
								</tr>`)
					}

				}
			});
		}

		function json2array(json) {
			var result = [];
			var keys = Object.keys(json);
			keys.forEach(function (key) {
				result.push(json[key]);
			});
			return result;
		}
		$('#add-row').click(function () {
			if (x >= 8)
				return;
			x = x + 1;
			col = `<td data-name="name" class='coly val'>
								<input type="number" name='name0' placeholder='0.0' class="form-control" value="0" />
				</td>`
			cols = col.repeat(y)
			row = `<tr id='addr0' data-id="0" class="hidden rowx val">
						<td data-name="name" class="text-center font-weight-bold text-responsive"> S${x-1} </td>${cols}</tr>`
			$('#table tr.val:last').after(row);
			update(x, 'row')
		})
		$('#add-col').click(function () {
			if (y >= 8)
				return;
			y = y + 1;
			$('#table tr:first th.b:last').after(`<th class="text-center b text-responsive"> D${y-1} </th> `);
			$('#table').find('tr.rowx').each(function () {
				$(this).find('td.val:last').after(
					`<td data-name="name" class='coly val'>
								<input type="number" name='name0' placeholder='0.0' class="form-control" value="0"/>
				</td>`);
			});
			update(y, 'col')
		})

		$('#remove-col').click(function () {
			if (y <= 3)
				return;
			y = y - 1;
			console.log(y)
			$('#table tr:first th.b:last').remove();
			$('#table').find('tr.rowx').each(function () {
				$(this).find('td.coly.val:last').remove();
			});
			update(y, 'col')
		})

		$('#remove-row').click(function () {
			if (x <= 3)
				return;
			x = x - 1;
			$('#table tr.rowx.val:last').remove();
			update(x, 'row')
		})

		function update(x, index) {
			if (x <= 3) {
				$('#remove-' + index).attr('disabled', true);
			} else if (x > 3 && x < 8) {
				$('#remove-' + index).attr('disabled', false);
				$('#add-' + index).attr('disabled', false);
			} else if (x >= 8)
				$('#add-' + index).attr('disabled', true);
		}
		$(document).ajaxSend(function (event, request, settings) {
			$('#loading-indicator').show();
			$('<div class="modal-backdrop"></div>').appendTo(document.body);
		});

		$(document).ajaxComplete(function (event, request, settings) {
			$('#loading-indicator').hide();
			$(".modal-backdrop").remove();
		});
	}