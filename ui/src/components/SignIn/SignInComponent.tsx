import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { FaUser, FaLock } from "react-icons/fa";
import logo from "../../assets/logo.png";
import { useNotification } from "../../hooks/useNotification";
import { fetchWithAuth } from "../../utils/api";

function SignIn() {
    const { showNotification } = useNotification();
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const [isSigning, setIsSigning] = useState(false);

    const navigate = useNavigate();

    const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
        e.preventDefault();
        setIsSigning(true);

        try {
            const response = await fetchWithAuth(`${import.meta.env.VITE_API_BASE_URL}/api/login`, {
                method: "POST",
                credentials: "include",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    email: username,
                    password: password
                }),
            });

            const data = await response.json();

            if (response.ok) {
                // 1. Sucessful alert
                showNotification({
                    type: "success",
                    title: "Login successful",
                    message: `Welcome ${data.name}!`,
                });

                // 2. Save user info to browser
                sessionStorage.setItem("userEmail", data.email);
                sessionStorage.setItem("userName", data.name);
                sessionStorage.setItem("userCredits", data.credits);
                // 3. Push user to Dashboard
                navigate("/dashboard");
            } else {
                showNotification({
                    type: "error",
                    title: "Login failed",
                    message: data.detail,
                });
            }
        } catch (error) {
            console.error("Connection error:", error);
            showNotification({
                type: "error",
                title: "Connection error",
                message: "Cannot connect to server Backend!",
            });
        } finally {
            setIsSigning(false);
        }
    };

    const isDisabled = username === "" || password === "" || isSigning;


    return (
        <div className="auth bg-rd-white text-rd-darkblue flex min-h-screen w-screen items-center justify-center">
            <form className="flex w-full max-w-[330px] flex-col items-center" onSubmit={handleSubmit}>
                <img
                    src={logo}
                    alt="logo"
                    className="mb-8 w-[100px] rounded-3xl border border-rd-lightgrey"
                />

                <div className="w-full">
                    {/* Email input */}
                    <div className="relative mb-4">
                        <div className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-4">
                            <FaUser className="text-rd-darkblue" size={18} />
                        </div>
                        <input
                            type="text"
                            placeholder="Email"
                            value={username}
                            onChange={(e) => setUsername(e.target.value)}
                            className="border-rd-lightgrey focus:border-rd-blue focus:ring-rd-blue w-full rounded-lg border bg-white py-4 pl-12 pr-3 text-sm transition-all focus:ring-1"
                        />
                    </div>

                    {/* Password input */}
                    <div className="relative mb-4">
                        <div className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-4">
                            <FaLock className="text-rd-darkblue" size={18} />
                        </div>
                        <input
                            type="password"
                            placeholder="Password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            className="border-rd-lightgrey focus:border-rd-blue focus:ring-rd-blue w-full rounded-lg border bg-white py-4 pl-12 pr-3 text-sm transition-all focus:ring-1"
                        />
                    </div>
                </div>

                <div className="w-full">
                    <button
                        type="submit"
                        disabled={isDisabled}
                        className="bg-rd-darkblue disabled:bg-rd-lightgrey mx-auto mt-4 h-[46px] w-full rounded-[0_1rem_0px_1rem] p-[10px] font-bold text-white transition-all hover:opacity-90 disabled:cursor-not-allowed"
                    >
                        {isSigning ? "Signing in..." : "Sign In"}
                    </button>

                    <div className="mt-4 flex w-full justify-end">
                        <Link
                            to="/signup"
                            className="text-rd-darkblue font-bold hover:underline"
                        >
                            Sign Up
                        </Link>
                    </div>
                </div>
            </form>
        </div>
    );
}

export default SignIn;