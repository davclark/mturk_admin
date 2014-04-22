# How to set up the surveys to get workerId

You need to put some javascript IN THE HIT, ultimately, I explain how I did this here:
http://www.askdav.com/stories/mturk-survey-experiments.html

But for now, you should be able to put only this in your HIT:

<script type="text/javascript"><!--
addEventListener('load', function() {
    // We now have an initial state where visibility is set in CSS
    var workerId_arg = '&workerId=' + turkGetParam('workerId', '');

    // This is for debugging, along with the commented span at the top
    // $("#workerId").text('Javascript detected worker ID "' + workerId + '"')
    var link_elt = document.getElementById('surveyLink');

    link_elt.href += workerId_arg;
});
--></script>

**Sadly, that doesn't seem to be reliable** - so it's probably best to have a
backup field in your HIT that asks for workerId (and explain that its for
followup).

You also need to set up Qualtrics to record the incoming workerId info from the
URL. You do this in Survey Flow (available in the top button bar when you're
editing your survey in Qualtrics).
