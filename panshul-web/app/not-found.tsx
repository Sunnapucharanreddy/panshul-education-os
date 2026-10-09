import Link from "next/link";

export default function NotFound() {
  return (
    <div className="page">
      <p className="kicker">404</p>
      <h1>That page is not on Panshul.</h1>
      <div className="row">
        <Link href="/" className="btn btn-primary">Back home</Link>
      </div>
    </div>
  );
}
