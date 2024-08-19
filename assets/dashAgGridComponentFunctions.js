let isChecked="";
let value=false;

var dagcomponentfuncs = window.dashAgGridComponentFunctions = window.dashAgGridComponentFunctions || {};

dagcomponentfuncs.Button = function (props) {
    const {setData, data} = props;

    const answer_array = props.value.split(":");
    var color = "#06ae0a"
    if(answer_array[0] === "Missed Lead")
    {
        color = "#f15a4d"
    }
    if(answer_array[0] === "Completed")
    {
        color = "#06ae0a"
    }
    if(answer_array[0] === "Potential Lead")
    {
        color = "#f4c13a"
    }

    return React.createElement(
        'button',
        {
            id: {"type": "analyse", "index": parseInt(answer_array[1])},
            style: {backgroundColor: color, width: "150px", height: "25px", borderColor: color, fontSize:"11px"},
            onClick: () => {console.log('clicked')},
            className: props.className,
        },
        answer_array[0]
    );
};

var dagcomponentfuncs = window.dashAgGridComponentFunctions = window.dashAgGridComponentFunctions || {};


dagcomponentfuncs.FlagsCellRenderer = function (props) {

   // for more info see https://flagpedia.net/
    const url = `https://flagcdn.com/h20/${props.data.country}.png`;

    return React.createElement('span', {}, [
        React.createElement(
            'img',
            {
                style: {height: '20px', width:'20px', borderRadius: '50%',marginTop:'-5px'},
                src: url
            },

        ),
        React.createElement(
            'span',
            {
                style: {paddingLeft: '10px'},
            },
            props.data.Customername
        ),
    ]);
};

var dagcomponentfuncs = window.dashAgGridComponentFunctions = window.dashAgGridComponentFunctions || {};


dagcomponentfuncs.CheckboxRenderer = function (props) {

   // for more info see https://flagpedia.net/
    const url = `https://flagcdn.com/h20/${props.data.country}.png`;

    return React.createElement('span', {}, [
        React.createElement(
            'input',
            {
                type: 'checkbox',
                style: {height: '20px', width:'20px', borderRadius: '50%',marginTop:'5px'},
                onChange: (event) => {
                    const checkboxes = document.querySelectorAll('input[type="checkbox"]');
                    const currentCheckbox = event.target;

                    // Uncheck all checkboxes except the current one
                    checkboxes.forEach((checkbox) => {
                        if (checkbox !== currentCheckbox) {
                            checkbox.checked = false;
                        }
                    });

                    const isChecked = currentCheckbox.checked;
                    const value = currentCheckbox.value;

                    console.log('Checkbox Value:', value, 'Is Checked:', isChecked);

                    const outputDiv = document.getElementById('output-div');
                    outputDiv.textContent = "Selected UUID: "+value;
                    const analyseDiv = document.getElementById('analyse');
                    analyseDiv.style = "display:inline-block";
                    // Trigger Dash callback by simulating an event
                    const eventChange = new Event('change');
                    outputDiv.dispatchEvent(eventChange);

                },
                value: props.data.UUID
            },

        ),
        React.createElement(
            'span',
            {
                style: {paddingLeft: '10px'},
            },
            props.data.UUID
        ),
    ]);
};
function ImageRenderer(params) {
    // Create a button element
    var button = document.createElement('button');
    button.className = 'btn btn-primary play-btn';
    button.innerText = 'Play';
    return button;
}