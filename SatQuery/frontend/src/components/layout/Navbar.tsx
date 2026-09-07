import logo from "../../assets/satquery-logo.jpeg";

const Navbar = () => {
  return (
    <nav className="navbar">
      <div className="logo">
        <img
          src={logo}
          alt="SatQuery AI logo"
          className="navbar-logo-image"
        />

        <span className="logo-name">
          G-Query <strong>AI</strong>
        </span>
      </div>
.

      <div className="nav-links">
        <a href="#">Home</a>
        <a href="#">History</a>
        <a href="#">About</a>
      </div>
    </nav>
  );
};

export default Navbar;