if (!$) {$ = django.jQuery;} // for use in the django admin site without specifying another jquery version

function getCookie(name) {
  var cookieValue = null;
  if (document.cookie && document.cookie != '') {
      var cookies = document.cookie.split(';');
      for (var i = 0; i < cookies.length; i++) {
          var cookie = $.trim(cookies[i]);
          // Does this cookie string begin with the name we want?
          if (cookie.substring(0, name.length + 1) == (name + '=')) {
              cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
              break;
          }
      }
  }
  return cookieValue;
}

var csrftoken = getCookie('csrftoken');

function csrfSafeMethod(method) {
  // these HTTP methods do not require CSRF protection
  return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

function build_reference(item) {
  const first_author = item.author[0].family + ', ' + item.author[0].given[0] + '.';
  const title = item.title.join(' ')
  return first_author + ', ' + title
}

function post_to_url() {
  $.post({
    url: $(this).data()['post-Url'], 
    data: parseJSON($(this).select2('data')[0]),
    success : function(result) {
        window.location.reload();
    },
    error: function(xhr, resp, text) {
        console.log(xhr, resp, text);
    }
  })
}

function parseJSON(item) {

  var output = {};
  Object.entries(item).forEach(function(field) {
    // replace hyphens with underscores
    field[0] = field[0].replace('-','_')

    // convert objects to string representations
    if (typeof field[1] == "object") {
      field[1] = JSON.stringify(field[1])
    }
    output[field[0]] = field[1]
  })

  return output
}

$(function () {

  const $select = $('#crossrefQuickAdd');

  $.ajaxSetup({
    beforeSend: function (xhr, settings) {
        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
  });

  $select.select2({
    // multiple: true,
    minimumInputLength: 1,
    ajax: {
      delay: 1000,
      data: function (params) {
        return {
          "query": params.term,
          "select": 'DOI,container-title',
          // "rows": '3',
          "mailto": 'jennings@gfz-potsdam.de',
        };
      },

      processResults: function (data) {
        return {
          results: $.map(data.message.items, function (item) {
            return {...item, ...{
              id: item[$select.data()['crossrefId']],
              text: item[$select.data()['crossrefName']], 
            }
          }})
        };
      }
    }
  });

  $select.on('change', post_to_url)


  $('#select2Opener').on('click', function(e) {
    e.preventDefault();
    $select.select2('open');
  })


})