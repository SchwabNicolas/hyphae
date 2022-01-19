import React, {useState} from "react";

class NodeComponent extends React.Component {
    render() {
        return (
            <button className="square">
                {this.props.value}
            </button>
        );
    }
}