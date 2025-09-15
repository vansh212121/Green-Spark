import { useEffect, useState } from "react";
import { useSelector } from "react-redux";
import { Outlet } from "react-router-dom";
import { selectAccessToken } from "@/features/authSlice";
import { useGetMeQuery } from "@/features/api/authApi";

const PersistLogin = () => {
  const accessToken = useSelector(selectAccessToken);
  const [checked, setChecked] = useState(false);

  // Kick off /me query only if we have a token
  const { isFetching, isError } = useGetMeQuery(undefined, {
    skip: !accessToken,
  });

  useEffect(() => {
    if (!isFetching) setChecked(true);
  }, [isFetching]);

  if (!checked) {
    return <p>Loading session...</p>;
  }

  return <Outlet />;
};

export default PersistLogin;
