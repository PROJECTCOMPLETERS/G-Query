import logo from "../../assets/satquery-logo.jpeg";

interface Props {
  onNew: () => void;
  onHistory: () => void;
  onAbout: () => void;
}

export default function Navbar({
  onNew,
  onHistory,
  onAbout,
}: Props) {
  return (
    <nav className="navbar">
      <button
        className="logo"
        onClick={onNew}
        aria-label="G-Query logo — new chat"
      >
        <img
          src={logo}
          alt=""
          className="navbar-logo-image"
        />

        <span className="logo-name">
          G-Query <strong>AI</strong>
        </span>
      </button>

      <div className="nav-links">
        <button onClick={onNew}>New chat</button>
        <button onClick={onHistory}>History</button>
        <button onClick={onAbout}>About</button>
      </div>
    </nav>
  );
}