"use client";

import { api, useAuth } from "@/contexts/auth-context";
import { useGoogleLogin } from "@react-oauth/google";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { FaCheck, FaGoogle, FaTimes } from "react-icons/fa";

export default function SignupPage() {
  const [email, setEmail] = useState("");
  const [name, setName] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [passwordValid, setPasswordValid] = useState(false);
  const [passwordMatch, setPasswordMatch] = useState(false);
  const [error, setError] = useState("");
  const [formValid, setFormValid] = useState(false);
  const [agreedToTerms, setAgreedToTerms] = useState(false);
  const { isAuthenticated } = useAuth();
  const router = useRouter();
  const [showSuccessPopup, setShowSuccessPopup] = useState(false);

  useEffect(() => {
    if (isAuthenticated && !showSuccessPopup) {
      router.push("/dashboard");
    }
  }, [isAuthenticated, router, showSuccessPopup]);

  useEffect(() => {
    setFormValid(
      email.trim() !== "" &&
        name.trim() !== "" &&
        passwordValid &&
        passwordMatch &&
        agreedToTerms
    );
  }, [email, name, passwordValid, passwordMatch, agreedToTerms]);

  const handlePasswordChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newPassword = e.target.value;
    setPassword(newPassword);
    setPasswordValid(newPassword.length >= 8);
    setPasswordMatch(newPassword === confirmPassword);
  };

  const handleConfirmPasswordChange = (
    e: React.ChangeEvent<HTMLInputElement>
  ) => {
    const newConfirmPassword = e.target.value;
    setConfirmPassword(newConfirmPassword);
    setPasswordMatch(password === newConfirmPassword);
  };

  const handleGoogleSignupSuccess = async (codeResponse: { code: string }) => {
    try {
      const { data } = await api.post(
        "/users/login/google",
        {
          code: codeResponse.code,
        },
        {
          headers: {
            "x-timezone": Intl.DateTimeFormat().resolvedOptions().timeZone,
          },
        }
      );
      setShowSuccessPopup(true);
    } catch (error) {
      console.error("Google signup failed:", error);
      setError(error instanceof Error ? error.message : "Signup failed");
    }
  };

  const googleSignup = useGoogleLogin({
    flow: "auth-code",
    onSuccess: handleGoogleSignupSuccess,
    onError: () => {
      console.error("Google signup failed");
      setError("Google signup failed");
    },
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    try {
      const { data } = await api.post(
        "/users/signup",
        {
          email,
          password,
          name,
        },
        {
          headers: {
            "x-timezone": Intl.DateTimeFormat().resolvedOptions().timeZone,
          },
        }
      );
      setShowSuccessPopup(true);
    } catch (err) {
      setError("Signup failed. Please try again.");
      setEmail("");
      setPassword("");
      setConfirmPassword("");
      setName("");
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center">
      {showSuccessPopup ? (
        <div className="fixed inset-0 bg-white flex items-center justify-center">
          <div className="p-6 rounded-lg max-w-sm w-full mx-4 text-center">
            <FaCheck className="mx-auto text-green-500 text-4xl mb-4" />
            <h3 className="text-xl font-semibold mb-2">
              Account Created Successfully!
            </h3>
            <p className="text-gray-600 mb-6">
              Your account has been created. Click below to sign in.
            </p>
            <button
              onClick={() => router.push("/login")}
              className="w-full bg-indigo-600 text-white py-2 px-4 rounded-md hover:bg-indigo-500 transition-colors"
            >
              Go to Login
            </button>
          </div>
        </div>
      ) : (
        <div className="w-full max-w-md space-y-8 p-8">
          <div className="text-center">
            <h2 className="text-3xl font-bold">Create your account</h2>
            <p className="mt-2 text-sm text-gray-600">
              Already have an account?{" "}
              <a
                href="/login"
                className="text-indigo-600 hover:text-indigo-500 font-medium"
              >
                Sign in here
              </a>
            </p>
          </div>

          <form onSubmit={handleSubmit} className="mt-8 space-y-6">
            <div className="space-y-4 rounded-md shadow-sm">
              <div>
                <label htmlFor="name" className="sr-only">
                  Full name
                </label>
                <input
                  id="name"
                  name="name"
                  type="text"
                  required
                  className="relative block w-full rounded-md border-0 p-2 text-gray-900 ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-indigo-600"
                  placeholder="Full name"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                />
              </div>

              <div>
                <label htmlFor="email" className="sr-only">
                  Email address
                </label>
                <input
                  id="email"
                  name="email"
                  type="email"
                  required
                  className="relative block w-full rounded-md border-0 p-2 text-gray-900 ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-indigo-600"
                  placeholder="Email address"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                />
              </div>

              <div>
                <label htmlFor="password" className="sr-only">
                  Password
                </label>
                <input
                  id="password"
                  name="password"
                  type="password"
                  required
                  className="relative block w-full rounded-md border-0 p-2 text-gray-900 ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-indigo-600"
                  placeholder="Password"
                  value={password}
                  onChange={handlePasswordChange}
                />
                {!passwordValid && (
                  <p className="text-sm text-gray-500 mt-1">
                    Password must be at least 8 characters long.
                  </p>
                )}
              </div>

              <div className="relative">
                <label htmlFor="confirmPassword" className="sr-only">
                  Confirm Password
                </label>
                <input
                  id="confirmPassword"
                  name="confirmPassword"
                  type="password"
                  required
                  className="relative block w-full rounded-md border-0 p-2 text-gray-900 ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-indigo-600"
                  placeholder="Confirm Password"
                  value={confirmPassword}
                  onChange={handleConfirmPasswordChange}
                />
                {confirmPassword && (
                  <span className="absolute right-3 top-1/2 -translate-y-1/2">
                    {passwordMatch ? (
                      <FaCheck className="text-green-500" />
                    ) : (
                      <FaTimes className="text-red-500" />
                    )}
                  </span>
                )}
              </div>
            </div>

            <div className="flex items-center">
              <input
                id="terms"
                name="terms"
                type="checkbox"
                className="h-4 w-4 rounded border-gray-300 text-indigo-600 focus:ring-indigo-600"
                checked={agreedToTerms}
                onChange={(e) => setAgreedToTerms(e.target.checked)}
                required
              />
              <label
                htmlFor="terms"
                className="ml-2 block text-sm text-gray-900"
              >
                I agree to the{" "}
                <a
                  href="/terms"
                  className="text-indigo-600 hover:text-indigo-500"
                >
                  Terms of Service
                </a>
              </label>
            </div>

            {error && (
              <div className="text-red-500 text-sm text-center">{error}</div>
            )}

            <button
              type="submit"
              disabled={!formValid}
              className="group relative flex w-full justify-center rounded-md bg-indigo-600 px-3 py-2 text-sm font-semibold text-white hover:bg-indigo-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Create account
            </button>
          </form>

          <div className="mt-6">
            <div className="relative">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-gray-300" />
              </div>
              <div className="relative flex justify-center text-sm">
                <span className="bg-white px-2 text-gray-500">
                  Or continue with
                </span>
              </div>
            </div>
            <div className="mt-6 flex justify-center">
              <button
                onClick={() => googleSignup()}
                className="flex items-center gap-2 px-4 py-2 border rounded-md hover:bg-gray-50"
              >
                <FaGoogle className="text-indigo-600" />
                Sign up with Google
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
