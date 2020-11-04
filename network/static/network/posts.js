document.addEventListener('DOMContentLoaded', () => {

    console.log("fertich");

    document.querySelectorAll('.edit').forEach(button => button.addEventListener('click', click_event => update_content(click_event.path[0])));

    document.querySelectorAll('.like').forEach(button => button.addEventListener('click', click_event => like_unlike(click_event.path[0])));
})


function update_content(button) {

    console.log(button);

    let body = document.querySelector('#content' + button.dataset.post).innerHTML;
    let form_id = 'button' + button.dataset.post;
    let text_input_id = 'input' + button.dataset.post;

    let old_source = document.querySelector('#post' + button.dataset.post).innerHTML;

    htmlSource = `
    <form id="${form_id}">
        <div id="New-Post">
            <input type="text" id="${text_input_id}" class="form-control" rows="3" value="${body}"></input>
        </div>
        <div id="New-Post-submit-button">
            <input type="submit" class="btn btn-light" value="Edit"></input>
        </div>
    </form>`;

    document.querySelector('#post' + button.dataset.post).innerHTML = htmlSource;

    document.querySelector('#' + form_id).addEventListener('submit', () => {
        console.log('in on submit');
        new_content = document.querySelector('#input' + button.dataset.post).value;

        fetch(`/post/${button.dataset.post}`, {
            method: "PUT",
            body: JSON.stringify({
                content: new_content
            })
        });

        console.log(new_content);

        document.querySelector('#post' + button.dataset.post).innerHTML = old_source;
        document.querySelector('#content' + button.dataset.post).innerHTML = new_content;

        return false;
    })
}


function like_unlike(button) {
    fetch(`/like/${button.dataset.post}`, {
        method: "POST"
    })
    .then(response => response.json())
    .then(result => {

        var num_likes = parseInt(document.querySelector(`#likes${button.dataset.post}`).innerHTML);

        if (result.is_increase === 'true') {
            document.querySelector(`#likes${button.dataset.post}`).innerHTML = num_likes + 1;
            document.querySelector(`#like_button${button.dataset.post}`).innerHTML = 'Un Like';
        }
        else {
            document.querySelector(`#likes${button.dataset.post}`).innerHTML = num_likes - 1;
            document.querySelector(`#like_button${button.dataset.post}`).innerHTML = 'Like';
        }
    });
}