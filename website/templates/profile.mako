<%inherit file="base.mako"/>
<%def name="title()">${profile["fullname"]}'s Profile</%def>

<%def name="javascript_bottom()">
% if user["is_profile"]:
    <script>
        $(function() {
            $('#profile-fullname').editable({
                type:  'text',
                pk:    '${profile["id"]}',
                name:  'fullname',
                url:   '/api/v1/profile/${profile["id"]}/edit/',
                title: 'Edit Full Name',
                placement: 'bottom',
                value: '${profile["fullname"]}',
                mode: "inline",
                success: function(data) {
                    // Also change the display name in the user info table
                    $(".fullname").text(data['name']);
                }
            });
        });
    </script>
% endif

</%def>

<%def name="content()">
% if profile['is_merged']:
<div class="alert alert-info">This account has been merged with <a class="alert-link" href="${profile['merged_by']['url']}">${profile['merged_by']['absolute_url']}</a>
</div>
% endif


<div class="page-header">
    <img src="${profile['gravatar_url']}" />
    <h1 id="profile-fullname" style="display:inline-block">${profile["fullname"]}</h1>
</div><!-- end-page-header -->

<div class="row">
    <div class="col-md-4">
        <table class="table table-plain">
            <tr>
              <td>Name</td>
              <td class="fullname">${profile["fullname"]}</td>
            </tr>
            <tr>
              <td>Member Since</td>
              <td>${profile['date_registered']}</td>
            </tr>
            <tr>
              <td>Public Profile</td>
              <td><a href="${profile['url']}">${profile['display_absolute_url']}</a></td>
            </tr>
        </table>
    </div>
    <div class="col-md-4 col-md-offset-4">
        <h2>
           ${profile['activity_points'] or "No"} activity point${'s' if profile['activity_points'] != 1 else ''}<br />
           ${profile["number_projects"]} project${'s' if profile["number_projects"] != 1  else ''}, ${profile["number_public_projects"]} public
        </h2>
    </div>
</div><!-- end row -->
<hr />

<div class="row">
    <div class="col-md-6">
        <h3>Public Projects</h3>
        <div mod-meta='{
                "tpl" : "util/render_nodes.mako",
                "uri" : "/api/v1/profile/${profile["id"]}/public_projects/",
                "replace" : true,
                "kwargs" : {"sortable" : true}
            }'></div>
    </div>
    <div class="col-md-6">
        <h3>Public Components</h3>
        <div mod-meta='{
                "tpl" : "util/render_nodes.mako",
                "uri" : "/api/v1/profile/${profile["id"]}/public_components/",
                "replace" : true,
                "kwargs" : {"sortable" : true}
            }'></div>
    </div>
</div><!-- end row -->

<%include file="log_templates.mako"/>
</%def>
