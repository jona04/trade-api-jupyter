import React from "react";
import NavBarLink from "./NavBarLink";

function NavigationBar() {

  return (
    <div id="navbar">
        <div className="navtitle">Forex Dash</div>
        <div id="navlinks">
            <NavBarLink path="/" text="Home" />
            <NavBarLink path="/dashboard" text="Dashboard" />
            <NavBarLink path="/backtest" text="Backtest" />
        </div>
    </div>
  );
}

export default NavigationBar;
