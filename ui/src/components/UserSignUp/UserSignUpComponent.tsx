/*
 * Copyright (c) 2024 Rapiddweller Asia Co., Ltd.
 * All rights reserved.
 *
 * This software and related documentation are provided under a license
 * agreement containing restrictions on use and disclosure and are
 * protected by intellectual property laws. Except as expressly permitted
 * in your license agreement or allowed by law, you may not use, copy,
 * reproduce, translate, broadcast, modify, license, transmit, distribute,
 * exhibit, perform, publish, or display any part, in any form, or by any means.
 *
 * This software is the confidential and proprietary information of
 * Rapiddweller Asia Co., Ltd. ("Confidential Information"). You shall not
 * disclose such Confidential Information and shall use it only in accordance
 * with the terms of the license agreement you entered into with Rapiddweller Asia Co., Ltd.
 *
 */

import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom"; // <-- add useNavigate
import logo from "../../assets/logo.png";
import { useNotification } from '../../hooks/useNotification';
import { fetchWithAuth } from "../../utils/api";
const UserSignUp = () => {
    const { showNotification } = useNotification();
    const [emailValue, setEmail] = useState("");
    const [firstName, setFirstName] = useState("");
    const [lastName, setLastName] = useState("");
    const [newPassword, setNewPassword] = useState("");
    const [confPass, setConfPass] = useState("");
    const [isSigning, setIsSigning] = useState(false); // <-- add state loading

    const navigate = useNavigate(); // <-- initialize navigate function

    // Condition to disable button: Missing info, password mismatch, or API is being called
    const isDisabled = !emailValue || !firstName || !newPassword || newPassword !== confPass || isSigning;

    // Change to async function to call real API
    const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
        e.preventDefault();
        setIsSigning(true);

        try {
            const response = await fetchWithAuth(`${import.meta.env.VITE_API_BASE_URL}/api/signup`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                // Package data to send to Backend (Map to Backend field names)
                body: JSON.stringify({
                    email: emailValue,
                    first_name: firstName,
                    last_name: lastName,
                    password: newPassword,
                }),
            });

            const data = await response.json();

            if (response.ok) {
                showNotification({
                    type: "success",
                    title: "Sign up successful",
                    message: `Welcome ${data.name}! Your account has been created with ${data.credits} Credits!`,

                });
                // Sign up successfully then navigate to Login page
                navigate("/login");
            } else {
                showNotification({
                    type: "error",
                    title: "Sign up failed",
                    message: data.detail,
                });
            }
        } catch (error) {
            console.error("Error:", error);
            showNotification({
                type: "error",
                title: "Connection error",
                message: "Cannot connect to server Backend!",
            });
        } finally {
            setIsSigning(false);
        }
    };


    return (
        <div className="auth bg-rd-white text-rd-darkblue">
            <div className="flex h-screen w-screen flex-col items-center justify-center">
                <img
                    src={logo}
                    alt="logo"
                    className="mt-[2rem] w-[100px] rounded-3xl border border-rd-lightgrey"
                />

                <div className="w-[330px] content-center p-[5px] text-center font-bold text-lg mt-4 mb-2">
                    <span>Create new User</span>
                </div>

                <div className="w-[330px]">
                    <form autoComplete="off" onSubmit={handleSubmit}>
                        <div className="flex flex-col gap-4">
                            <input
                                type="email"
                                placeholder="Email"
                                value={emailValue}
                                onChange={(e) => setEmail(e.target.value)}
                                className="px-4 w-full py-4 text-sm bg-white border border-rd-lightgrey rounded-lg focus:border-rd-blue"
                            />
                            <input
                                type="text"
                                placeholder="First Name"
                                value={firstName}
                                onChange={(e) => setFirstName(e.target.value)}
                                className="px-4 w-full py-4 text-sm bg-white border border-rd-lightgrey rounded-lg focus:border-rd-blue"
                            />
                            <input
                                type="text"
                                placeholder="Last Name"
                                value={lastName}
                                onChange={(e) => setLastName(e.target.value)}
                                className="px-4 w-full py-4 text-sm bg-white border border-rd-lightgrey rounded-lg focus:border-rd-blue"
                            />
                            <input
                                type="password"
                                placeholder="Password"
                                value={newPassword}
                                onChange={(e) => setNewPassword(e.target.value)}
                                className="px-4 w-full py-4 text-sm bg-white border border-rd-lightgrey rounded-lg focus:border-rd-blue"
                            />
                            <input
                                type="password"
                                placeholder="Confirm Password"
                                value={confPass}
                                onChange={(e) => setConfPass(e.target.value)}
                                className="px-4 w-full py-4 text-sm bg-white border border-rd-lightgrey rounded-lg focus:border-rd-blue"
                            />
                            {confPass && newPassword !== confPass && (
                                <p className="text-rd-flashred text-sm mt-[-10px]">Passwords do not match</p>
                            )}
                        </div>

                        <button
                            type="submit"
                            disabled={isDisabled}
                            className="bg-rd-darkblue mx-auto mt-[2rem] h-[46px] w-full rounded-[0_1rem_0px_1rem] p-[10px] font-bold text-white transition-all hover:opacity-90 disabled:cursor-not-allowed disabled:bg-rd-lightgrey"
                        >
                            {isSigning ? "Submitting..." : "Submit"}
                        </button>

                        <div className="flex w-full justify-center mt-4">
                            <Link to="/login" className="text-rd-darkblue text-sm hover:underline">
                                Already have an account? Sign In
                            </Link>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    );
};

export default UserSignUp;